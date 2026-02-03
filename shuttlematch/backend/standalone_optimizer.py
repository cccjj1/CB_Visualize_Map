#!/usr/bin/env python3
"""
Campus Shuttle Optimization System - Standalone Version
Combines improved genetic algorithm and real project simulation features
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass
import random

# Data Models
@dataclass
class Request:
    """Passenger Travel Request"""
    request_id: str
    student_id: str
    origin_stop_id: str
    dest_stop_id: str
    eta: str
    boarding_time: str
    early_tol: int
    late_tol: int

@dataclass
class Stop:
    """Campus Service Stop"""
    stop_id: str
    name: str
    lat: float
    lng: float
    stop_type: str = 'CAMPUS'

@dataclass
class Trip:
    """车次行程"""
    trip_id: str
    vehicle_id: str
    start_time: str
    end_time: str
    start_stop_id: str
    end_stop_id: str
    duration_minutes: float
    passenger_count: int
    route: List[str]

@dataclass
class Assignment:
    """乘客分配"""
    request_id: str
    trip_id: str
    boarding_stop_id: str
    alighting_stop_id: str
    promised_eta: str
    actual_eta: str
    boarding_time: str
    alighting_time: str

@dataclass
class RouteCandidate:
    """路线候选方案"""
    requests: List[Request]
    route: List[str]
    total_duration: float
    passenger_satisfaction: float
    feasibility_score: float

class ImprovedGeneticOptimizer:
    """改进的遗传算法优化器 - 基于顺路逻辑"""
    
    def __init__(self, 
                 requests: List[Request],
                 stops: List[Stop],
                 time_matrix: np.ndarray,
                 capacity: int = 12,
                 min_passengers: int = 8,
                 max_vehicles: int = 20,
                 population_size: int = 50,
                 generations: int = 100,
                 mutation_rate: float = 0.15,
                 max_detour_factor: float = 1.5,
                 max_route_duration: int = 120):
        """
        初始化改进的遗传算法优化器
        
        Args:
            requests: 乘客请求列表
            stops: 站点列表
            time_matrix: 时间矩阵
            capacity: 车辆容量
            min_passengers: 最小载客数
            max_vehicles: 最大车辆数
            population_size: 种群大小
            generations: 进化代数
            mutation_rate: 变异率
            max_detour_factor: 最大绕行倍数
            max_route_duration: 最大路线时长（分钟）
        """
        self.requests = requests
        self.stops = stops
        self.time_matrix = time_matrix
        self.capacity = capacity
        self.min_passengers = min_passengers
        self.max_vehicles = max_vehicles
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.max_detour_factor = max_detour_factor
        self.max_route_duration = max_route_duration
        
        # Create mapping from stop ID to index
        self.stop_id_to_index = {stop.stop_id: i for i, stop in enumerate(stops)}
        
        # Pre-calculate direct travel time for all requests
        self._precompute_direct_times()
        
        # Create rideshare groups
        self._create_route_groups()
    
    def _precompute_direct_times(self):
        """预计算所有请求的直达时间"""
        self.direct_times = {}
        for request in self.requests:
            from_idx = self.stop_id_to_index[request.origin_stop_id]
            to_idx = self.stop_id_to_index[request.dest_stop_id]
            self.direct_times[request.request_id] = self.time_matrix[from_idx][to_idx]
    
    def _create_route_groups(self):
        """创建顺路群组"""
        self.route_groups = []
        
        # Group by origin
        origin_groups = {}
        for request in self.requests:
            origin = request.origin_stop_id
            if origin not in origin_groups:
                origin_groups[origin] = []
            origin_groups[origin].append(request)
        
        # Create rideshare groups for each origin
        for origin, requests in origin_groups.items():
            if len(requests) >= self.min_passengers:
                # Group by destination similarity
                dest_groups = self._group_by_destination_similarity(requests)
                for dest_group in dest_groups:
                    if len(dest_group) >= self.min_passengers:
                        self.route_groups.append(dest_group)
        
        print(f"✅ 创建了 {len(self.route_groups)} 个顺路群组")
    
    def _group_by_destination_similarity(self, requests: List[Request]) -> List[List[Request]]:
        """按目的地相似性分组"""
        if len(requests) <= self.capacity:
            return [requests]
        
        # Cluster by destination
        dest_groups = {}
        for request in requests:
            dest = request.dest_stop_id
            if dest not in dest_groups:
                dest_groups[dest] = []
            dest_groups[dest].append(request)
        
        # Merge similar destination groups
        groups = []
        for dest, group_requests in dest_groups.items():
            if len(group_requests) >= self.min_passengers:
                groups.append(group_requests)
            else:
                # Find similar destinations to merge
                merged = False
                for i, existing_group in enumerate(groups):
                    if self._are_destinations_similar(group_requests, existing_group):
                        groups[i].extend(group_requests)
                        merged = True
                        break
                if not merged:
                    groups.append(group_requests)
        
        return groups
    
    def _are_destinations_similar(self, group1: List[Request], group2: List[Request]) -> bool:
        """判断两个群组的目的地是否相似"""
        dest1 = set(req.dest_stop_id for req in group1)
        dest2 = set(req.dest_stop_id for req in group2)
        
        # If destinations overlap, consider similar
        return len(dest1.intersection(dest2)) > 0
    
    def optimize(self) -> Tuple[List[Trip], List[Assignment]]:
        """执行优化"""
        print("🧬 开始改进的遗传算法优化...")
        
        # Initialize population
        population = self._initialize_population()
        
        best_solution = None
        best_fitness = -float('inf')
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                fitness = self._evaluate_fitness(individual)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_solution = individual
            
            # Selection, crossover, mutation
            new_population = []
            
            # Elitism
            elite_count = max(1, self.population_size // 10)
            elite_indices = np.argsort(fitness_scores)[-elite_count:]
            for idx in elite_indices:
                new_population.append(population[idx])
            
            # Generate new individuals
            while len(new_population) < self.population_size:
                # Selection
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                
                # Crossover
                child1, child2 = self._crossover(parent1, parent2)
                
                # Mutation
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.population_size]
            
            if generation % 10 == 0:
                print(f"  🧬 第 {generation+1}/{self.generations} 代... 最佳适应度: {best_fitness:.4f}")
        
        # Decode best solution
        trips, assignments = self._decode_solution(best_solution)
        
        print(f"✅ 改进的遗传算法优化完成!")
        print(f"   - 最终适应度: {best_fitness:.4f}")
        print(f"   - 生成车次: {len(trips)}")
        print(f"   - 分配乘客: {len(assignments)}")
        
        return trips, assignments
    
    def _initialize_population(self) -> List[List[int]]:
        """初始化种群"""
        population = []
        
        for _ in range(self.population_size):
            # Create individual: request order for each group
            individual = []
            for group in self.route_groups:
                group_indices = [self.requests.index(req) for req in group]
                random.shuffle(group_indices)
                individual.extend(group_indices)
            
            # Add ungrouped requests
            ungrouped_requests = []
            for req in self.requests:
                if not any(req in group for group in self.route_groups):
                    ungrouped_requests.append(self.requests.index(req))
            
            random.shuffle(ungrouped_requests)
            individual.extend(ungrouped_requests)
            
            population.append(individual)
        
        return population
    
    def _evaluate_fitness(self, individual: List[int]) -> float:
        """评估个体适应度"""
        try:
            trips, assignments = self._decode_solution(individual)
            
            if not trips:
                return 0.0
            
            # Check vehicle count constraint
            if len(trips) > self.max_vehicles:
                return -1.0
            
            # Calculate fitness components
            service_rate = len(assignments) / len(self.requests)
            
            # Occupancy rate
            total_passengers = sum(trip.passenger_count for trip in trips)
            load_factor = total_passengers / (len(trips) * self.capacity)
            
            # Passenger satisfaction
            satisfaction_scores = []
            for assignment in assignments:
                request = next(req for req in self.requests if req.request_id == assignment.request_id)
                direct_time = self.direct_times[request.request_id]
                actual_time = self._calculate_ride_time(assignment)
                detour_factor = actual_time / direct_time if direct_time > 0 else 1.0
                
                # Satisfaction: less detour is better
                satisfaction = max(0, 1 - (detour_factor - 1) / self.max_detour_factor)
                satisfaction_scores.append(satisfaction)
            
            passenger_satisfaction = np.mean(satisfaction_scores) if satisfaction_scores else 0.0
            
            # Route efficiency
            total_duration = sum(trip.duration_minutes for trip in trips)
            avg_duration = total_duration / len(trips) if len(trips) > 0 else 0
            route_efficiency = 1 / (1 + avg_duration / 60)  # Convert to hours
            
            # Combined fitness
            fitness = (
                0.4 * service_rate +
                0.3 * passenger_satisfaction +
                0.2 * load_factor +
                0.1 * route_efficiency
            )
            
            return fitness
            
        except Exception as e:
            return 0.0
    
    def _calculate_ride_time(self, assignment: Assignment) -> float:
        """计算乘客乘车时间"""
        boarding_minutes = self._time_to_minutes(assignment.boarding_time)
        alighting_minutes = self._time_to_minutes(assignment.alighting_time)
        return alighting_minutes - boarding_minutes
    
    def _decode_solution(self, individual: List[int]) -> Tuple[List[Trip], List[Assignment]]:
        """解码个体为路线和分配"""
        trips = []
        assignments = []
        trip_counter = 1
        
        # Process requests by individual order
        current_trip_requests = []
        
        for request_idx in individual:
            request = self.requests[request_idx]
            current_trip_requests.append(request)
            
            # Check if valid route can be formed
            if len(current_trip_requests) >= self.min_passengers:
                # Check vehicle count constraint
                if trip_counter > self.max_vehicles:
                    break
                
                # Attempt to create route
                trip, trip_assignments = self._create_route_from_requests(current_trip_requests, trip_counter)
                
                if trip is not None:
                    trips.append(trip)
                    assignments.extend(trip_assignments)
                    trip_counter += 1
                    current_trip_requests = []
                else:
                    # If cannot create valid route, try reducing request count
                    for i in range(len(current_trip_requests) - 1, self.min_passengers - 1, -1):
                        reduced_requests = current_trip_requests[:i]
                        trip, trip_assignments = self._create_route_from_requests(reduced_requests, trip_counter)
                        if trip is not None:
                            trips.append(trip)
                            assignments.extend(trip_assignments)
                            trip_counter += 1
                            current_trip_requests = current_trip_requests[i:]
                            break
        
        return trips, assignments
    
    def _create_route_from_requests(self, requests: List[Request], trip_id: int) -> Tuple[Trip, List[Assignment]]:
        """从请求创建路线 - 基于顺路逻辑"""
        if len(requests) < self.min_passengers:
            return None, []
        
        # Check route feasibility
        if not self._check_route_feasibility(requests):
            return None, []
        
        # Build optimized route
        route = self._build_optimized_route(requests)
        if not route:
            return None, []
        
        # Calculate route duration
        total_duration = self._calculate_route_duration(route)
        
        # Check route length constraint
        if total_duration > self.max_route_duration:
            return None, []
        
        # Calculate departure time
        departure_time = self._calculate_departure_time(requests, total_duration)
        arrival_time = self._calculate_arrival_time(departure_time, total_duration)
        
        # Create route object
        trip = Trip(
            trip_id=f"IGA{trip_id:06d}",
            vehicle_id=f"V{trip_id:06d}",
            start_time=departure_time,
            end_time=arrival_time,
            start_stop_id=route[0],
            end_stop_id=route[-1],
            duration_minutes=total_duration,
            passenger_count=len(requests),
            route=route
        )
        
        # Create assignment
        assignments = self._create_assignments(requests, trip, route)
        
        return trip, assignments
    
    def _check_route_feasibility(self, requests: List[Request]) -> bool:
        """检查路线可行性 - 顺路逻辑"""
        if len(requests) < 2:
            return True
        
        # Check direct travel time for all passengers
        direct_times = [self.direct_times[req.request_id] for req in requests]
        max_direct_time = max(direct_times)
        
        # If direct time too long, consider unreasonable
        if max_direct_time > 45:  # Relaxed to 45 minutes
            return False
        
        # Check origin concentration
        origins = [req.origin_stop_id for req in requests]
        unique_origins = len(set(origins))
        
        # If origins too dispersed, consider unreasonable
        if unique_origins > len(requests) * 0.9:  # Relaxed to 90%
            return False
        
        # Check destination concentration
        destinations = [req.dest_stop_id for req in requests]
        unique_destinations = len(set(destinations))
        
        # If destinations too dispersed, consider unreasonable
        if unique_destinations > len(requests) * 0.9:  # Relaxed to 90%
            return False
        
        return True
    
    def _build_optimized_route(self, requests: List[Request]) -> List[str]:
        """构建优化路线 - 基于顺路逻辑"""
        if not requests:
            return []
        
        # Collect all stops to visit
        all_stops = set()
        for request in requests:
            all_stops.add(request.origin_stop_id)
            all_stops.add(request.dest_stop_id)
        
        # Use improved greedy algorithm
        route = []
        remaining_stops = list(all_stops)
        
        # Select starting point: stop with earliest boarding time
        start_stops = [req.origin_stop_id for req in requests]
        start_times = [self._time_to_minutes(req.boarding_time) for req in requests]
        start_stop = start_stops[start_times.index(min(start_times))]
        
        route.append(start_stop)
        remaining_stops.remove(start_stop)
        
        # Greedy selection of next stop
        current_stop = start_stop
        while remaining_stops:
            min_distance = float('inf')
            next_stop = None
            
            for stop in remaining_stops:
                from_idx = self.stop_id_to_index[current_stop]
                to_idx = self.stop_id_to_index[stop]
                distance = self.time_matrix[from_idx][to_idx]
                
                if distance < min_distance:
                    min_distance = distance
                    next_stop = stop
            
            if next_stop:
                route.append(next_stop)
                remaining_stops.remove(next_stop)
                current_stop = next_stop
            else:
                break
        
        return route
    
    def _calculate_route_duration(self, route: List[str]) -> float:
        """计算路线行驶时间"""
        if len(route) < 2:
            return 0
        
        total_time = 0
        for i in range(len(route) - 1):
            from_idx = self.stop_id_to_index[route[i]]
            to_idx = self.stop_id_to_index[route[i + 1]]
            total_time += self.time_matrix[from_idx][to_idx]
        
        return total_time
    
    def _calculate_departure_time(self, requests: List[Request], total_duration: float) -> str:
        """计算发车时间"""
        # Based on earliest request time
        earliest_eta = min(self._time_to_minutes(req.eta) for req in requests)
        departure_minutes = earliest_eta - total_duration
        
        # Ensure departure time is not negative
        if departure_minutes < 0:
            departure_minutes = 0
        
        return self._minutes_to_time(departure_minutes)
    
    def _calculate_arrival_time(self, departure_time: str, total_duration: float) -> str:
        """计算到达时间"""
        departure_minutes = self._time_to_minutes(departure_time)
        arrival_minutes = departure_minutes + total_duration
        return self._minutes_to_time(arrival_minutes)
    
    def _create_assignments(self, requests: List[Request], trip: Trip, route: List[str]) -> List[Assignment]:
        """创建分配"""
        assignments = []
        
        # Calculate arrival time at each stop in route
        departure_minutes = self._time_to_minutes(trip.start_time)
        stop_arrival_times = {}
        current_time = departure_minutes
        
        for stop_id in route:
            stop_arrival_times[stop_id] = current_time
            # Assume 2 minutes stop at each stop
            current_time += 2
        
        # Create assignment for each passenger
        for request in requests:
            # Get passenger expected boarding time
            expected_boarding_minutes = self._time_to_minutes(request.boarding_time)
            
            # Get actual arrival time in route
            route_boarding_time = stop_arrival_times.get(request.origin_stop_id, departure_minutes)
            route_alighting_time = stop_arrival_times.get(request.dest_stop_id, current_time)
            
            # Use expected time as base, but ensure within route time range
            boarding_time_minutes = max(expected_boarding_minutes, route_boarding_time)
            alighting_time_minutes = max(boarding_time_minutes + 1, route_alighting_time)
            
            # Check alighting time window constraint
            promised_minutes = self._time_to_minutes(request.eta)
            early_tol = request.early_tol
            late_tol = request.late_tol
            
            # Adjust alighting time to reasonable range
            if alighting_time_minutes < promised_minutes - early_tol:
                alighting_time_minutes = promised_minutes - early_tol
            elif alighting_time_minutes > promised_minutes + late_tol:
                alighting_time_minutes = promised_minutes + late_tol
            
            # Ensure boarding time not later than alighting time
            if boarding_time_minutes > alighting_time_minutes:
                boarding_time_minutes = alighting_time_minutes - 1
            
            boarding_time = self._minutes_to_time(boarding_time_minutes)
            alighting_time = self._minutes_to_time(alighting_time_minutes)
            
            assignment = Assignment(
                request_id=request.request_id,
                trip_id=trip.trip_id,
                boarding_stop_id=request.origin_stop_id,
                alighting_stop_id=request.dest_stop_id,
                promised_eta=request.eta,
                actual_eta=alighting_time,
                boarding_time=boarding_time,
                alighting_time=alighting_time
            )
            assignments.append(assignment)
        
        return assignments
    
    def _tournament_selection(self, population: List[List[int]], fitness_scores: List[float], tournament_size: int = 3) -> List[int]:
        """锦标赛选择"""
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_idx]
    
    def _crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """交叉操作"""
        if len(parent1) != len(parent2):
            return parent1, parent2
        
        # Single-point crossover
        crossover_point = random.randint(1, len(parent1) - 1)
        
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        
        return child1, child2
    
    def _mutate(self, individual: List[int]) -> List[int]:
        """变异操作"""
        if random.random() < self.mutation_rate:
            # Randomly swap two positions
            if len(individual) >= 2:
                i, j = random.sample(range(len(individual)), 2)
                individual[i], individual[j] = individual[j], individual[i]
        
        return individual
    
    def _time_to_minutes(self, time_str: str) -> int:
        """将时间字符串转换为分钟"""
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute
    
    def _minutes_to_time(self, minutes: int) -> str:
        """将分钟转换为时间字符串"""
        minutes = int(minutes) % (24 * 60)  # Ensure within 24 hours
        hour = minutes // 60
        minute = minutes % 60
        return f"{hour:02d}:{minute:02d}"

def load_data():
    """加载数据"""
    print("📥 加载数据...")
    
    # Load stop data
    stops_df = pd.read_csv('/Users/samuel/Desktop/campus_bus_optimization/Project_mocking_Input/lat-lon.csv')
    stops = []
    stop_name_to_id = {}
    
    for idx, row in stops_df.iterrows():
        stop_id = f"STOP_{idx+1:03d}"
        stop_name_to_id[row['Name']] = stop_id
        stop = Stop(
            stop_id=stop_id,
            name=row['Name'],
            lat=row['Latitude'],
            lng=row['Longitude'],
            stop_type='CAMPUS'
        )
        stops.append(stop)
    
    print(f"✅ 站点数据加载完成: {len(stops)} 个站点")
    
    # Load request data
    requests_df = pd.read_csv('/Users/samuel/Desktop/campus_bus_optimization/Project_mocking_Input/mock_request.csv')
    requests = []
    
    for idx, (_, row) in enumerate(requests_df.iterrows()):
        # Map stop names to IDs (remove leading/trailing spaces)
        origin_name = row['origin_stop_id'].strip()
        dest_name = row['dest_stop_id'].strip()
        origin_id = stop_name_to_id.get(origin_name)
        dest_id = stop_name_to_id.get(dest_name)
        
        if origin_id and dest_id:
            request = Request(
                request_id=f"R{idx+1:06d}",
                student_id=str(row['student_id']),
                origin_stop_id=origin_id,
                dest_stop_id=dest_id,
                eta=row['eta'],
                boarding_time=row['boarding_time'],
                early_tol=row['early_tol'],
                late_tol=row['late_tol']
            )
            requests.append(request)
    
    print(f"✅ 请求数据加载完成: {len(requests)} 个请求")
    
    # Load time matrix
    time_matrix_df = pd.read_csv('/Users/samuel/Desktop/campus_bus_optimization/Project_mocking_Input/matrix_12x12_time (1).csv', index_col=0)
    # Clean spaces in column and index names
    time_matrix_df.columns = [col.strip() for col in time_matrix_df.columns]
    time_matrix_df.index = [idx.strip() for idx in time_matrix_df.index]
    time_matrix = time_matrix_df.values
    
    print(f"✅ 时间矩阵加载完成: {time_matrix.shape[0]}x{time_matrix.shape[1]}")
    
    return requests, stops, time_matrix

def save_results(trips, assignments, requests, stops):
    """保存结果到CSV文件"""
    print("💾 保存CSV文件...")
    
    # Ensure output directory exists
    os.makedirs('data/output', exist_ok=True)
    
    # Create mapping from request_id to student_id
    request_id_to_student_id = {req.request_id: req.student_id for req in requests}
    
    # Save route information
    trips_data = []
    for trip in trips:
        trips_data.append({
            'trip_id': trip.trip_id,
            'vehicle_id': trip.vehicle_id,
            'start_time': trip.start_time,
            'end_time': trip.end_time,
            'start_stop_id': trip.start_stop_id,
            'end_stop_id': trip.end_stop_id,
            'duration_minutes': trip.duration_minutes,
            'passenger_count': trip.passenger_count,
            'route': ' → '.join(trip.route)
        })
    
    trips_df = pd.DataFrame(trips_data)
    trips_df.to_csv('data/output/real_project_trips.csv', index=False)
    print(f"✅ 路线信息已保存: data/output/real_project_trips.csv")
    
    # Save assignment information
    assignments_data = []
    for assignment in assignments:
        student_id = request_id_to_student_id.get(assignment.request_id, '')
        assignments_data.append({
            'request_id': assignment.request_id,
            'trip_id': assignment.trip_id,
            'boarding_stop_id': assignment.boarding_stop_id,
            'alighting_stop_id': assignment.alighting_stop_id,
            'promised_eta': assignment.promised_eta,
            'actual_eta': assignment.actual_eta,
            'boarding_time': assignment.boarding_time,
            'alighting_time': assignment.alighting_time,
            'student_id': student_id
        })
    
    assignments_df = pd.DataFrame(assignments_data)
    assignments_df.to_csv('data/output/real_project_assignments.csv', index=False)
    print(f"✅ 分配信息已保存: data/output/real_project_assignments.csv")
    
    # Generate passenger matching results
    generate_passenger_matching_results(assignments_df, requests)
    
    # Generate request format output
    generate_requests_output(requests, assignments_df)

def generate_passenger_matching_results(assignments_df, requests):
    """生成乘客匹配结果CSV"""
    # Read original request data
    requests_df = pd.read_csv('/Users/samuel/Desktop/campus_bus_optimization/Project_mocking_Input/mock_request.csv')
    
    # Create matching results
    matching_results = []
    for _, row in requests_df.iterrows():
        student_id = row['student_id']
        
        # Find matching assignment
        matched_assignment = assignments_df[assignments_df['student_id'] == student_id]
        
        if not matched_assignment.empty:
            assignment = matched_assignment.iloc[0]
            matching_results.append({
                'student_id': student_id,
                'matched': True,
                'trip_id': assignment['trip_id'],
                'pickup_time': assignment['boarding_time'],
                'arrive_time': assignment['alighting_time'],
                'request_date': '2025-10-27'
            })
        else:
            matching_results.append({
                'student_id': student_id,
                'matched': False,
                'trip_id': '',
                'pickup_time': '',
                'arrive_time': '',
                'request_date': '2025-10-27'
            })
    
    # Save matching results
    matching_df = pd.DataFrame(matching_results)
    matching_df.to_csv('data/output/real_project_passenger_matching_results.csv', index=False)
    print(f"✅ 乘客匹配结果已保存: data/output/real_project_passenger_matching_results.csv")

def generate_requests_output(requests, assignments_df):
    """生成请求格式的输出文件"""
    print("📋 生成请求格式输出文件...")
    
    # Create request output data
    requests_output = []
    
    for request in requests:
        # Find assignment info for this request
        assignment = assignments_df[assignments_df['request_id'] == request.request_id]
        
        if not assignment.empty:
            # If assigned
            actual_assignment = assignment.iloc[0]
            requests_output.append({
                'uid': request.student_id,
                'matched': True,
                'pickup_time': actual_assignment['boarding_time'],
                'arrive_time': actual_assignment['actual_eta'],
                'request_date': '2025-10-27'
            })
        else:
            # If not assigned
            requests_output.append({
                'uid': request.student_id,
                'matched': False,
                'pickup_time': '',
                'arrive_time': '',
                'request_date': '2025-10-27'
            })
    
    # Save request output
    requests_df = pd.DataFrame(requests_output)
    requests_df.to_csv('data/output/requests_output.csv', index=False)
    print(f"✅ 请求格式输出已保存: data/output/requests_output.csv")
    
    return requests_df

def main():
    """主函数"""
    print("🚌 校园定制公交优化系统 - 独立完整版")
    print("="*60)
    
    try:
        # Load data
        requests, stops, time_matrix = load_data()
        
        # Create optimizer
        optimizer = ImprovedGeneticOptimizer(
            requests=requests,
            stops=stops,
            time_matrix=time_matrix,
            capacity=12,
            min_passengers=4,  # Reduce minimum passenger count
            max_vehicles=30,   # Increase maximum vehicle count
            population_size=100,
            generations=100,
            mutation_rate=0.15,
            max_detour_factor=2.0  # Relax detour limit
        )
        
        # Execute optimization
        trips, assignments = optimizer.optimize()
        
        # Save results
        save_results(trips, assignments, requests, stops)
        
        print(f"\n✅ 优化完成!")
        print(f"   - 生成路线: {len(trips)} 条")
        print(f"   - 服务乘客: {len(assignments)} 人")
        print(f"   - 服务率: {len(assignments)/len(requests)*100:.1f}%")
        print(f"   - 输出文件: data/output/")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

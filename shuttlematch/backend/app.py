import pandas as pd
import os
from datetime import datetime, timedelta
import random
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177", "http://localhost:5178", "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175", "http://127.0.0.1:5176", "http://127.0.0.1:5177", "http://127.0.0.1:5178"]}})

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
MOCK_REQUEST_FILE = os.path.join(DATA_DIR, 'mock_request.csv')
MATCHES_FILE = os.path.join(DATA_DIR, 'matches.csv')
TIME_MATRIX_FILE = os.path.join(DATA_DIR, 'matrix_12x12_time.csv')
SHUTTLE_ROUTES_FILE = os.path.join(DATA_DIR, 'shuttle_routes.csv')

os.makedirs(DATA_DIR, exist_ok=True)

# Load time matrix
time_matrix_df = pd.read_csv(TIME_MATRIX_FILE, index_col=0)
# Clean column and index names (remove whitespace)
time_matrix_df.columns = [col.strip() for col in time_matrix_df.columns]
time_matrix_df.index = [idx.strip() for idx in time_matrix_df.index]

def get_travel_time(origin, destination):
    """Get travel time between two locations from the matrix"""
    try:
        travel_time = time_matrix_df.loc[origin, destination]
        return int(travel_time)
    except KeyError:
        return 25  # Default value

@app.route('/route_time', methods=['GET'])
def get_route_time():
    """Get travel time between two locations"""
    from_loc = request.args.get('from')
    to_loc = request.args.get('to')

    if not from_loc or not to_loc:
        return jsonify({'error': 'missing_parameters'}), 400

    try:
        time = time_matrix_df.loc[from_loc, to_loc]
        return jsonify({'time': int(time)})
    except KeyError:
        return jsonify({'error': 'invalid_route', 'message': 'Invalid route'}), 400

@app.route('/match', methods=['POST'])
def match_request():
    data = request.get_json()

    # Validate required fields
    required_fields = ['uid', 'origin', 'destination', 'earliest_arrival', 'latest_arrival']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'missing_fields'}), 400

    # Validate origin and destination are different
    if data['origin'] == data['destination']:
        return jsonify({'error': 'same_location', 'message': 'Origin and destination cannot be the same'}), 400

    # Validate time format and range
    try:
        earliest = datetime.strptime(data['earliest_arrival'], '%H:%M')
        latest = datetime.strptime(data['latest_arrival'], '%H:%M')
        if earliest > latest:
            return jsonify({'error': 'invalid_time_range'}), 400
    except ValueError:
        return jsonify({'error': 'invalid_time_format'}), 400

    # Calculate boarding_time
    travel_time = get_travel_time(data['origin'], data['destination'])
    random_reduction = random.randint(5, 15)  # Randomly reduce by 5-15 minutes
    
    try:
        eta_time = datetime.strptime(data['earliest_arrival'], '%H:%M')
        boarding_time_dt = eta_time - timedelta(minutes=travel_time) - timedelta(minutes=random_reduction)
        boarding_time = boarding_time_dt.strftime('%H:%M')
    except ValueError:
        boarding_time = data['earliest_arrival']

    # Generate random tolerances
    early_tol = random.randint(5, 15)
    late_tol = random.randint(5, 15)

    # Create new request record
    new_request = {
        'student_id': data['uid'],
        'origin_stop_id': data['origin'],
        'dest_stop_id': data['destination'],
        'eta': data['earliest_arrival'],
        'boarding_time': boarding_time,
        'early_tol': early_tol,
        'late_tol': late_tol,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Append to mock_request.csv
    try:
        if os.path.exists(MOCK_REQUEST_FILE):
            existing_df = pd.read_csv(MOCK_REQUEST_FILE)
            new_df = pd.concat([existing_df, pd.DataFrame([new_request])], ignore_index=True)
        else:
            new_df = pd.DataFrame([new_request])
        
        new_df.to_csv(MOCK_REQUEST_FILE, index=False)
        
        return jsonify({
            'status': 'success',
            'message': 'Booking request submitted successfully',
            'data': {
                'boarding_time': boarding_time,
                'travel_time': travel_time,
                'early_tol': early_tol,
                'late_tol': late_tol
            }
        })
    except Exception as e:
        print(f"Error saving request: {str(e)}")
        return jsonify({'error': 'save_failed', 'message': 'Failed to save booking'}), 500

@app.route('/result/<uid>', methods=['GET'])
def get_result(uid):
    try:
        # First, read all original request data
        mock_df = pd.read_csv(MOCK_REQUEST_FILE)
        user_mock_requests = mock_df[(mock_df['student_id'] == uid)]
        
        if len(user_mock_requests) == 0:
            # No booking records
            return jsonify({'results': [], 'message': 'No booking records found'})
        
        # Read matching results
        matches_df = pd.read_csv(MATCHES_FILE)
        user_matches = matches_df[(matches_df['student_id'] == uid)]
        
        # Load shuttle routes for mapping
        routes_df = None
        if os.path.exists(SHUTTLE_ROUTES_FILE):
            routes_df = pd.read_csv(SHUTTLE_ROUTES_FILE)
        
        # Return matching results
        results = []
        
        # Iterate through all requests
        for req_idx, req_row in user_mock_requests.iterrows():
            result = {
                'origin': req_row['origin_stop_id'],
                'destination': req_row['dest_stop_id'],
                'created_at': req_row['timestamp'],
                'matched': False,  # Default: not matched
            }
            
            # Look for corresponding matching result
            if len(user_matches) > 0:
                # Find matching record with corresponding index
                if req_idx in user_matches.index:
                    match_row = user_matches.loc[req_idx]
                    # Convert matched field to boolean properly
                    matched_val = match_row['matched']
                    if isinstance(matched_val, str):
                        result['matched'] = matched_val.strip().lower() == 'true'
                    else:
                        result['matched'] = bool(matched_val)
                    
                    # Return pickup time and arrival time only if matched
                    if result['matched']:
                        result['pickup_time'] = match_row['pickup_time']
                        result['arrive_time'] = match_row['arrive_time']
                        
                        # Find the shuttle route for this passenger using trip_id
                        trip_id = str(match_row.get('trip_id', '')).strip()
                        if trip_id and routes_df is not None and len(routes_df) > 0:
                            try:
                                # Find route by trip_id
                                route_rows = routes_df[routes_df['trip_id'] == trip_id]
                                if len(route_rows) > 0:
                                    route_row = route_rows.iloc[0]
                                    result['shuttle_info'] = {
                                        'trip_id': route_row['trip_id'],
                                        'vehicle_id': route_row['vehicle_id'],
                                        'start_stop': route_row['start_stop'],
                                        'end_stop': route_row['end_stop'],
                                        'route_sequence': route_row['route_sequence'],
                                        'passenger_count': int(route_row['passenger_count']),
                                        'duration_minutes': int(route_row['duration_minutes']),
                                        'shuttle_start_time': route_row['start_time'],
                                        'shuttle_end_time': route_row['end_time']
                                    }
                            except Exception as e:
                                print(f"Error getting shuttle route for trip {trip_id}: {str(e)}")
            
            results.append(result)
        
        return jsonify({
            'results': results,
            'message': f'Found {len(results)} booking records'
        })
            
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return jsonify({'results': [], 'message': 'No booking records found'})
    except Exception as e:
        print(f"Error getting result: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'query_failed', 'message': 'Query failed'}), 500

@app.route('/request/<uid>', methods=['DELETE'])
def delete_request_handler(uid):
    try:
        # Read and update mock_request.csv
        if os.path.exists(MOCK_REQUEST_FILE):
            df = pd.read_csv(MOCK_REQUEST_FILE)
            initial_rows = len(df)
            df = df[df['student_id'] != uid]
            if len(df) < initial_rows:
                df.to_csv(MOCK_REQUEST_FILE, index=False)
                
                # Also delete matching results
                try:
                    matches_df = pd.read_csv(MATCHES_FILE)
                    matches_df = matches_df[matches_df['student_id'] != uid]
                    matches_df.to_csv(MATCHES_FILE, index=False)
                except (FileNotFoundError, pd.errors.EmptyDataError):
                    pass
                
                return jsonify({'status': 'success', 'message': 'Booking cancelled'})
        
        return jsonify({'error': 'not_found', 'message': 'Booking record not found'}), 404
        
    except Exception as e:
        print(f"Error deleting request: {str(e)}")
        return jsonify({'error': 'delete_failed', 'message': 'Failed to cancel booking'}), 500

@app.route('/shuttle_routes', methods=['GET'])
def get_shuttle_routes():
    """Get all shuttle routes information"""
    try:
        if not os.path.exists(SHUTTLE_ROUTES_FILE):
            return jsonify({'routes': [], 'message': 'No shuttle routes available'}), 404
        
        routes_df = pd.read_csv(SHUTTLE_ROUTES_FILE)
        routes = routes_df.to_dict('records')
        
        return jsonify({
            'routes': routes,
            'message': f'Retrieved {len(routes)} shuttle routes',
            'count': len(routes)
        })
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return jsonify({'routes': [], 'message': 'No shuttle routes available'}), 404
    except Exception as e:
        print(f"Error getting shuttle routes: {str(e)}")
        return jsonify({'error': 'query_failed', 'message': 'Failed to query shuttle routes'}), 500

@app.route('/route_map/<trip_id>', methods=['GET'])
def get_route_map(trip_id):
    """Get map URL for a specific route"""
    try:
        routes_file = SHUTTLE_ROUTES_FILE
        if not os.path.exists(routes_file):
            return jsonify({'error': 'not_found', 'message': 'No shuttle routes available'}), 404
        
        routes_df = pd.read_csv(routes_file)
        route = routes_df[routes_df['trip_id'] == trip_id]
        
        if len(route) == 0:
            return jsonify({'error': 'not_found', 'message': f'Route {trip_id} not found'}), 404
        
        try:
            from map_generator import GoogleMapsGenerator
            
            api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            if not api_key:
                return jsonify({'error': 'no_api_key', 'message': 'Google Maps API key not configured'}), 500
            
            generator = GoogleMapsGenerator(api_key)
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            lat_lon_file = os.path.join(data_dir, 'lat-lon.csv')
            locations = generator.load_locations(lat_lon_file)
            
            route_record = route.iloc[0].to_dict()
            map_url = generator.generate_route_url(route_record, locations)
            
            return jsonify({
                'trip_id': trip_id,
                'map_url': map_url,
                'route': route_record
            })
        except ImportError:
            return jsonify({'error': 'map_generator_unavailable', 'message': 'Map generation not available'}), 500
        
    except Exception as e:
        print(f"Error getting route map: {str(e)}")
        return jsonify({'error': 'query_failed', 'message': 'Failed to get route map'}), 500

@app.route('/all_routes_map', methods=['GET'])
def get_all_routes_map():
    """Get map URL showing all shuttle routes"""
    try:
        routes_file = SHUTTLE_ROUTES_FILE
        if not os.path.exists(routes_file):
            return jsonify({'error': 'not_found', 'message': 'No shuttle routes available'}), 404
        
        try:
            from map_generator import GoogleMapsGenerator
            
            api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            if not api_key:
                return jsonify({'error': 'no_api_key', 'message': 'Google Maps API key not configured'}), 500
            
            generator = GoogleMapsGenerator(api_key)
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            lat_lon_file = os.path.join(data_dir, 'lat-lon.csv')
            routes_df = pd.read_csv(routes_file)
            
            locations = generator.load_locations(lat_lon_file)
            routes = routes_df.to_dict('records')
            map_url = generator.generate_all_routes_url(routes, locations)
            
            return jsonify({
                'map_url': map_url,
                'total_routes': len(routes),
                'total_stops': len(locations)
            })
        except ImportError:
            return jsonify({'error': 'map_generator_unavailable', 'message': 'Map generation not available'}), 500
        
    except Exception as e:
        print(f"Error getting all routes map: {str(e)}")
        return jsonify({'error': 'query_failed', 'message': 'Failed to get all routes map'}), 500

@app.route('/map/<trip_id>', methods=['GET'])
def get_map_image(trip_id):
    """Get map image for a specific route"""
    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        maps_dir = os.path.join(data_dir, 'maps')
        map_file = os.path.join(maps_dir, f'{trip_id}.png')
        
        if not os.path.exists(map_file):
            return jsonify({'error': 'not_found', 'message': f'Map for {trip_id} not found'}), 404
        
        return send_file(map_file, mimetype='image/png')
    except Exception as e:
        print(f"Error getting map image: {str(e)}")
        return jsonify({'error': 'error', 'message': 'Failed to get map image'}), 500

@app.route('/all_routes_map/image', methods=['GET'])
def get_all_routes_map_image():
    """Get the overall map image showing all routes"""
    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        maps_dir = os.path.join(data_dir, 'maps')
        map_file = os.path.join(maps_dir, 'all_routes.png')
        
        if not os.path.exists(map_file):
            return jsonify({'error': 'not_found', 'message': 'Overall map not found'}), 404
        
        return send_file(map_file, mimetype='image/png')
    except Exception as e:
        print(f"Error getting all routes map image: {str(e)}")
        return jsonify({'error': 'error', 'message': 'Failed to get map image'}), 500

@app.route('/maps/list', methods=['GET'])
def list_maps():
    """List all available route maps"""
    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        maps_dir = os.path.join(data_dir, 'maps')
        
        if not os.path.exists(maps_dir):
            return jsonify({'maps': [], 'message': 'No maps available'})
        
        map_files = [f for f in os.listdir(maps_dir) if f.endswith('.png')]
        routes_df = pd.read_csv(SHUTTLE_ROUTES_FILE)
        
        maps_info = []
        for map_file in sorted(map_files):
            trip_id = map_file.replace('.png', '')
            if trip_id != 'all_routes':
                # Find corresponding route info
                route = routes_df[routes_df['trip_id'] == trip_id]
                if len(route) > 0:
                    r = route.iloc[0]
                    maps_info.append({
                        'trip_id': trip_id,
                        'filename': map_file,
                        'url': f'/map/{trip_id}',
                        'start_stop': r['start_stop'],
                        'end_stop': r['end_stop'],
                        'passenger_count': int(r['passenger_count']),
                        'duration_minutes': int(r['duration_minutes'])
                    })
            else:
                maps_info.append({
                    'name': 'All Routes Overview',
                    'filename': 'all_routes.png',
                    'url': '/all_routes_map/image'
                })
        
        return jsonify({
            'maps': maps_info,
            'total': len(map_files),
            'message': f'Found {len(maps_info)} maps'
        })
    except Exception as e:
        print(f"Error listing maps: {str(e)}")
        return jsonify({'error': 'error', 'message': 'Failed to list maps'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
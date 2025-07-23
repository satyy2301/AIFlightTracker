from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from config import config
import json
from datetime import datetime
app = Flask(__name__)
app.config['AVIATIONSTACK_API_KEY'] = config.AVIATIONSTACK_API_KEY
app.config['OPENROUTER_API_KEY'] = config.OPENROUTER_API_KEY
app.config['SECRET_KEY'] = config.SECRET_KEY
def get_flight_data(origin, destination, date):
    """Fetch flight data from AviationStack API"""
    try:
        params = {
            'access_key': app.config['AVIATIONSTACK_API_KEY'],
             'limit':100
        }
        # Use HTTPS instead of HTTP
        response = requests.get('https://api.aviationstack.com/v1/flights', params=params)
        
        # Print response for debugging (remove in production)
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Content: {response.text}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Error response: {e.response.text}")
        return None

def process_flight_data(data):
    """Process raw flight data into structured format with additional metrics"""
    if not data or 'data' not in data:
        return None
    
    processed_flights = []
    for flight in data['data']:
        processed_flights.append({
            'flight_number': flight.get('flight', {}).get('number', 'N/A'),
            'departure_airport': flight.get('departure', {}).get('airport', 'N/A'),
            'departure_time': flight.get('departure', {}).get('scheduled', 'N/A'),
            'arrival_airport': flight.get('arrival', {}).get('airport', 'N/A'),
            'arrival_time': flight.get('arrival', {}).get('scheduled', 'N/A'),
            'airline': flight.get('airline', {}).get('name', 'N/A'),
            'status': flight.get('flight_status', 'unknown')
        })
    
    return processed_flights

def generate_insights(data):
    """Generate professional, structured insights with predictive analysis"""
    if not data:
        return {
            "overview": "No flight data available for analysis",
            "recommendations": []
        }
    
    try:
        df = pd.DataFrame(data)
        
        # Basic statistics
        total_flights = len(df)
        status_counts = df['status'].value_counts(normalize=True).to_dict()
        
        # Time analysis
        df['departure_time'] = pd.to_datetime(df['departure_time'])
        df['hour'] = df['departure_time'].dt.hour
        hourly_dist = df['hour'].value_counts().sort_index()
        peak_hour = hourly_dist.idxmax()
        off_peak_hour = hourly_dist.idxmin()
        
        # Airline analysis
        airline_dist = df['airline'].value_counts(normalize=True)
        top_airline = airline_dist.idxmax()
        top_airline_share = airline_dist.max()
        
        # Flight duration analysis (if arrival time available)
        duration_analysis = ""
        if 'arrival_time' in df.columns:
            try:
                df['arrival_time'] = pd.to_datetime(df['arrival_time'])
                df['duration'] = (df['arrival_time'] - df['departure_time']).dt.total_seconds() / 60
                avg_duration = df['duration'].mean()
                duration_analysis = f"Average flight duration: {avg_duration:.1f} minutes"
            except:
                duration_analysis = "Flight duration data unavailable"

        # Predictive insights
        demand_level = "high" if total_flights > 15 else "moderate" if total_flights > 8 else "low"
        cancellation_risk = "low" if status_counts.get('cancelled', 0) < 0.1 else "medium" if status_counts.get('cancelled', 0) < 0.2 else "high"
        
        # Structured insights
        insights = {
            "overview": {
                "total_flights": total_flights,
                "time_period": f"{df['departure_time'].min().strftime('%H:%M')} to {df['departure_time'].max().strftime('%H:%M')}",
                "duration_analysis": duration_analysis,
                "demand_level": demand_level
            },
            "performance_metrics": {
                "on_time_performance": 1 - status_counts.get('delayed', 0) - status_counts.get('cancelled', 0),
                "cancellation_rate": status_counts.get('cancelled', 0),
                "peak_hour": f"{peak_hour}:00 - {peak_hour+1}:00",
                "off_peak_hour": f"{off_peak_hour}:00 - {off_peak_hour+1}:00"
            },
            "market_share": {
                "top_airline": {
                    "name": top_airline,
                    "share": f"{top_airline_share:.1%}",
                    "flights": airline_dist[top_airline]
                },
                "other_airlines": [
                    {"name": k, "share": f"{v:.1%}"} 
                    for k,v in airline_dist.nlargest(3).items() 
                    if k != top_airline
                ]
            },
            "recommendations": [
                {
                    "category": "Booking Strategy",
                    "suggestions": [
                        f"Book during off-peak hours ({off_peak_hour}:00) for better availability" if demand_level == "high" else "Flexible booking recommended",
                        "Consider early morning flights for higher reliability" if peak_hour > 12 else "Evening flights show more availability"
                    ]
                },
                {
                    "category": "Airline Selection",
                    "suggestions": [
                        f"Prefer {top_airline} for most options ({top_airline_share:.1%} of flights)",
                        "Compare alternatives for potential better pricing" if len(airline_dist) > 1 else "Limited airline options available"
                    ]
                },
                {
                    "category": "Risk Management",
                    "suggestions": [
                        f"Cancellation risk is {cancellation_risk} ({status_counts.get('cancelled', 0):.1%} of flights)",
                        "Consider travel insurance" if cancellation_risk in ["medium", "high"] else "Cancellation risk appears minimal"
                    ]
                }
            ],
            "predictive_insights": [
                f"Expected {demand_level} demand based on {total_flights} scheduled flights",
                "Higher probability of delays during peak hours" if peak_hour in [7,8,17,18] else "Generally stable operations expected",
                "Best pricing typically available 3-6 weeks before departure"  # Generic industry insight
            ]
        }
        
        return insights
        
    except Exception as e:
        print(f"Error generating insights: {e}")
        return {
            "overview": "Analysis unavailable due to data processing error",
            "recommendations": []
        }

def local_analysis(data):
    """Generate basic insights without external API"""
    if not data:
        return "No data available for analysis."
    
    df = pd.DataFrame(data)
    
    # Calculate basic statistics
    total_flights = len(df)
    status_counts = df['status'].value_counts().to_dict()
    
    # Time-based analysis
    df['departure_time'] = pd.to_datetime(df['departure_time'])
    df['hour'] = df['departure_time'].dt.hour
    busiest_hour = df['hour'].mode()[0]
    
    # Popular airlines
    popular_airlines = df['airline'].value_counts().nlargest(3).to_dict()
    
    # Generate insights text
    insights = [
        f"Analysis of {total_flights} flights:",
        "",
        "Flight Status Distribution:",
        *[f"- {status}: {count} flights" for status, count in status_counts.items()],
        "",
        f"Busiest Departure Hour: {busiest_hour}:00",
        "",
        "Most Frequent Airlines:",
        *[f"- {airline}: {count} flights" for airline, count in popular_airlines.items()],
        "",
        "Recommendations:",
        "- Consider offering promotions during less busy hours",
        "- Partner with popular airlines for better deals",
        "- Monitor flight status trends for operational improvements"
    ]
    
    return '\n'.join(insights)

def openrecruiter_analysis(data):
    """Generate insights using OpenRecruiter API"""
    try:
        response = requests.post(
            'https://api.openrecruiter.com/analyze',  # Hypothetical endpoint
            headers={'Authorization': f'Bearer {app.config["OPENRECRUITER_API_KEY"]}'},
            json={'data': data}
        )
        response.raise_for_status()
        return response.json().get('insights', 'No insights generated')
    except Exception as e:
        print(f"OpenRecruiter API error: {e}")
        return local_analysis(data)  # Fallback to local analysis

def create_visualizations(data):
    """Create professional visualization plots from the data"""
    if not data:
        return None
    
    # Set professional style (fallback if seaborn is not available)
    try:
        plt.style.use('seaborn-v0_8')  # Newer seaborn style name
    except:
        plt.style.use('ggplot')  # Fallback to ggplot style
    
    # Convert to DataFrame safely
    try:
        df = pd.DataFrame.from_records(data)
        
        # Calculate metrics
        metrics = {}
        if not df.empty:
            try:
                df['departure_time'] = pd.to_datetime(df['departure_time'])
                df['hour'] = df['departure_time'].dt.hour
                metrics['peak_hour'] = df['hour'].mode()[0] if not df['hour'].mode().empty else None
                metrics['top_airline'] = df['airline'].mode()[0] if not df['airline'].mode().empty else None
                metrics['on_time_rate'] = round((df['status'].isin(['scheduled', 'landed']).sum() / len(df)) * 100) if len(df) > 0 else 0
            except Exception as e:
                print(f"Error calculating metrics: {e}")
                metrics = {
                    'peak_hour': None,
                    'top_airline': None,
                    'on_time_rate': None
                }
    except Exception as e:
        print(f"Error creating DataFrame: {e}")
        return None
    
    # Plot 1: Flights by departure time
    plt.figure(figsize=(10, 5))
    hourly_counts = df['hour'].value_counts().sort_index()
    
    ax1 = hourly_counts.plot(kind='bar', color='#4e79a7', width=0.8)
    plt.title('Flights by Departure Hour', fontsize=14, pad=20)
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Number of Flights', fontsize=12)
    plt.xticks(rotation=0, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels if space permits
    max_val = hourly_counts.max()
    for i, v in enumerate(hourly_counts):
        if v > max_val * 0.1:  # Only label if there's enough space
            ax1.text(i, v + max_val * 0.02, str(v), 
                    ha='center', 
                    va='bottom',
                    fontsize=9)
    
    plt.tight_layout()
    buf1 = BytesIO()
    plt.savefig(buf1, format='png', dpi=120, bbox_inches='tight')
    plt.close()
    
    # Plot 2: Flight status distribution
    plt.figure(figsize=(8, 5))
    status_counts = df['status'].value_counts()
    
    colors = {
        'scheduled': '#4e79a7',
        'active': '#59a14f',
        'landed': '#edc948',
        'cancelled': '#e15759',
        'unknown': '#bab0ac'
    }
    
    color_list = [colors.get(status, '#bab0ac') for status in status_counts.index]
    
    wedges, texts, autotexts = plt.pie(
        status_counts,
        labels=status_counts.index if len(status_counts) <= 5 else None,
        autopct=lambda p: f'{p:.1f}%' if p > 5 else '',
        startangle=90,
        colors=color_list,
        textprops={'fontsize': 10},
        wedgeprops={'edgecolor': 'white', 'linewidth': 0.5},
        pctdistance=0.85
    )
    
    plt.title('Flight Status Distribution', fontsize=14, pad=20)
    
    # Add legend if needed
    if len(status_counts) > 3:
        plt.legend(
            wedges,
            status_counts.index,
            title="Status",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=9
        )
    
    plt.tight_layout()
    buf2 = BytesIO()
    plt.savefig(buf2, format='png', dpi=120, bbox_inches='tight')
    plt.close()
    
    return {
        'hourly_flights': base64.b64encode(buf1.getvalue()).decode('utf-8'),
        'status_distribution': base64.b64encode(buf2.getvalue()).decode('utf-8'),
        **metrics
    }

@app.route('/')
def index():
    """Render the main search page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process the search request and display results"""
    origin = request.form.get('origin', '').upper()
    destination = request.form.get('destination', '').upper()
    date = request.form.get('date', datetime.today().strftime('%Y-%m-%d'))
    
    # Get flight data
    raw_data = get_flight_data(origin, destination, date)
    processed_data = process_flight_data(raw_data)
    
    # Generate visualizations and insights
    visualizations = create_visualizations(processed_data) if processed_data else None
    insights = generate_insights(processed_data) if processed_data else None
    
    return render_template('results.html', 
                         origin=origin,
                         destination=destination,
                         date=date,
                         flights=processed_data,
                         visualizations=visualizations,
                         insights=insights)

@app.route('/api/flights', methods=['GET'])
def api_flights():
    """API endpoint for flight data"""
    origin = request.args.get('origin', '').upper()
    destination = request.args.get('destination', '').upper()
    date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    
    raw_data = get_flight_data(origin, destination, date)
    processed_data = process_flight_data(raw_data)
    
    return jsonify({
        'status': 'success',
        'data': processed_data
    })

if __name__ == '__main__':
    app.run(debug=True) 
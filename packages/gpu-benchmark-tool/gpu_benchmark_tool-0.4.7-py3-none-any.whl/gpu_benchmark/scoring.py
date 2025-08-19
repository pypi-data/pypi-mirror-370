# Enhanced scoring with all metrics

def score_gpu_health(baseline_temp, max_temp, power_draw, utilization, 
                    throttled=False, errors=False, throttle_events=None, 
                    temperature_stability=None, enhanced_metrics=None):
    """
    Enhanced GPU health scoring
    
    Returns:
        tuple: (score, status, recommendation, detailed_breakdown)
    """
    
    score = 0
    breakdown = {}
    
    # Temperature scoring (20 points max)
    temp_score = 0
    if max_temp != -1:
        if max_temp < 80: 
            temp_score = 20
        elif max_temp < 85: 
            temp_score = 15
        elif max_temp < 90: 
            temp_score = 10
        else:
            temp_score = 5
    breakdown["temperature"] = temp_score
    
    # Baseline temperature (10 points max)
    baseline_score = 0
    if baseline_temp != -1 and baseline_temp < 50: 
        baseline_score = 10
    elif baseline_temp != -1 and baseline_temp < 60: 
        baseline_score = 5
    breakdown["baseline_temp"] = baseline_score
    
    # Power efficiency (10 points max)
    power_score = 0
    if power_draw != -1:
        # This should be adjusted based on GPU TDP
        if 65 <= power_draw <= 70: 
            power_score = 10
        elif 60 <= power_draw < 65 or 70 < power_draw <= 75: 
            power_score = 5
    breakdown["power_efficiency"] = power_score
    
    # Utilization (10 points max)
    util_score = 0
    if utilization >= 99: 
        util_score = 10
    elif utilization >= 90: 
        util_score = 5
    breakdown["utilization"] = util_score
    
    # Throttling (20 points max)
    throttle_score = 20
    if throttle_events:
        # Deduct points based on throttle severity
        throttle_count = len(throttle_events)
        if throttle_count > 10:
            throttle_score = 0
        elif throttle_count > 5:
            throttle_score = 10
        elif throttle_count > 0:
            throttle_score = 15
    elif throttled:
        throttle_score = 0
    breakdown["throttling"] = throttle_score
    
    # Error handling (20 points max)
    error_score = 20
    if errors:
        if isinstance(errors, list):
            error_count = len(errors)
            if error_count > 5:
                error_score = 0
            elif error_count > 2:
                error_score = 10
            elif error_count > 0:
                error_score = 15
        else:
            error_score = 0
    breakdown["errors"] = error_score
    
    # Temperature stability (10 points max) - NEW
    stability_score = 0
    if temperature_stability:
        stability = temperature_stability.get("stability_score", 0)
        if stability >= 90:
            stability_score = 10
        elif stability >= 70:
            stability_score = 7
        elif stability >= 50:
            stability_score = 5
    breakdown["temperature_stability"] = stability_score
    
    # Calculate total score
    score = sum(breakdown.values())
    
    # Determine status and recommendation
    if score >= 85:
        status = "healthy"
        recommendation = "GPU is performing excellently. Safe for all workloads including training."
    elif score >= 70:
        status = "good"
        recommendation = "GPU is performing well. Suitable for most workloads."
    elif score >= 55:
        status = "degraded"
        recommendation = "GPU showing signs of stress. Limit to inference or light compute."
    elif score >= 40:
        status = "warning"
        recommendation = "GPU performance is concerning. Monitor closely and avoid heavy workloads."
    else:
        status = "critical"
        recommendation = "GPU is in poor condition. Do not deploy for production workloads."
    
    # Add specific recommendations based on weak areas
    specific_recommendations = []
    
    if breakdown["temperature"] < 10:
        specific_recommendations.append("High temperatures detected. Check cooling system.")
    
    if breakdown["throttling"] < 20:
        specific_recommendations.append("Throttling detected. May need better cooling or power delivery.")
    
    if breakdown["utilization"] < 5:
        specific_recommendations.append("Low GPU utilization. Workload may not be optimized.")
    
    if breakdown["temperature_stability"] < 5:
        specific_recommendations.append("Temperature instability detected. Check thermal paste and mounting.")
    
    return score, status, recommendation, {
        "breakdown": breakdown,
        "specific_recommendations": specific_recommendations,
        "max_score": 100
    }

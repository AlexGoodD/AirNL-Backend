def compute_aqi_pm25(concentration: float) -> tuple[int, str]:
    """
    Convierte concentración de PM2.5 (µg/m³) a AQI + categoría.
    Basado en tablas EPA/SINAICA.
    """
    breakpoints = [
    (0.0, 12.0,   0,  50,  "Good"),
    (12.1, 35.4,  51, 100, "Moderate"),
    (35.5, 55.4, 101, 150, "Unhealthy for Sensitive Groups"),
    (55.5, 150.4,151, 200, "Unhealthy"),
    (150.5, 250.4,201, 300,"Very Unhealthy"),
    (250.5, 500.0,301, 500,"Hazardous"),
]

    for c_low, c_high, aqi_low, aqi_high, category in breakpoints:
        if c_low <= concentration <= c_high:
            aqi = ((aqi_high - aqi_low) / (c_high - c_low)) * (concentration - c_low) + aqi_low
            return round(aqi), category

    return 500, "Extremadamente mala"
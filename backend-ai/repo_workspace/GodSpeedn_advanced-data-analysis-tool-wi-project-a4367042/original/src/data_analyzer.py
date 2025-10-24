
def data_analyzer():
    """Advanced data analysis tool"""
    import pandas as pd
    import numpy as np
    
    def analyze_data(data):
        """Analyze data and return insights"""
        if isinstance(data, list):
            data = pd.Series(data)
        
        analysis = {
            'mean': data.mean(),
            'median': data.median(),
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'count': len(data)
        }
        return analysis
    
    def generate_report(data, title="Data Analysis Report"):
        """Generate a comprehensive analysis report"""
        analysis = analyze_data(data)
        
        report = f"""
# {title}

## Summary Statistics
- **Count**: {analysis['count']}
- **Mean**: {analysis['mean']:.2f}
- **Median**: {analysis['median']:.2f}
- **Standard Deviation**: {analysis['std']:.2f}
- **Range**: {analysis['min']:.2f} to {analysis['max']:.2f}

## Data Quality
- **Completeness**: {100 - (data.isnull().sum() / len(data) * 100):.1f}%
- **Outliers**: {len(data[(data < analysis['mean'] - 2*analysis['std']) | (data > analysis['mean'] + 2*analysis['std'])])} detected

## Recommendations
1. Review outliers for data quality issues
2. Consider data transformation if distribution is skewed
3. Validate data collection process
        """
        return report.strip()
    
    return analyze_data, generate_report

if __name__ == "__main__":
    analyzer, reporter = data_analyzer()
    
    # Example usage
    sample_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 100]
    result = analyzer(sample_data)
    report = reporter(sample_data, "Sample Data Analysis")
    
    print("Analysis Results:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print("
Generated Report:")
    print(report)

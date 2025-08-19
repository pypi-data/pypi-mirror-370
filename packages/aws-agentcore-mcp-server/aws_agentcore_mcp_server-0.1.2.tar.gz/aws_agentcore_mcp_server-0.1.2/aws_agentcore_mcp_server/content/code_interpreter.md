# AgentCore Code Interpreter

AgentCore Code Interpreter allows AI agents to write and execute code securely within sandboxed sessions, enabling dynamic problem-solving and iterative computations.

## Key Features

- **Sandboxed Execution**: Secure code execution environment
- **Multiple Languages**: Support for Python, JavaScript, and more
- **Session Management**: Maintain context across multiple code executions
- **Library Support**: Pre-installed popular libraries (pandas, matplotlib, numpy, etc.)
- **File System Access**: Read/write files within the sandbox
- **Network Isolation**: Controlled network access for security

## Basic Usage

### Setting Up Code Interpreter
```python
from bedrock_agentcore.tools.code_interpreter_client import code_session
from strands import Agent, tool
import json

@tool
def execute_python(code: str, description: str = "") -> str:
    """Execute Python code in a secure sandbox."""
    if description:
        code = f"# {description}\n{code}"
    
    with code_session("us-west-2") as code_client:
        response = code_client.invoke("executeCode", {
            "code": code,
            "language": "python",
            "clearContext": False
        })
        
        for event in response["stream"]:
            if "result" in event:
                return json.dumps(event["result"])
```

### Data Analysis Example
```python
@tool
def analyze_data(data_description: str) -> str:
    """Analyze data using pandas and matplotlib."""
    code = f"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# {data_description}
# Create sample data for demonstration
data = {{
    'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'sales': [1000, 1200, 1100, 1300, 1500, 1400],
    'expenses': [800, 900, 850, 950, 1000, 950]
}}

df = pd.DataFrame(data)
print("Data Summary:")
print(df.describe())

# Create visualization
plt.figure(figsize=(10, 6))
plt.plot(df['month'], df['sales'], marker='o', label='Sales')
plt.plot(df['month'], df['expenses'], marker='s', label='Expenses')
plt.title('Monthly Sales vs Expenses')
plt.xlabel('Month')
plt.ylabel('Amount ($)')
plt.legend()
plt.grid(True)
plt.savefig('sales_analysis.png')
plt.show()

# Calculate profit
df['profit'] = df['sales'] - df['expenses']
print("\\nProfit Analysis:")
print(df[['month', 'profit']])
print(f"\\nTotal Profit: ${df['profit'].sum()}")
"""
    
    with code_session("us-west-2") as code_client:
        response = code_client.invoke("executeCode", {
            "code": code,
            "language": "python",
            "clearContext": False
        })
        
        result = ""
        for event in response["stream"]:
            if "result" in event:
                result += str(event["result"])
        
        return result
```

## Advanced Features

### File Operations
```python
@tool
def process_csv_file(file_content: str, filename: str) -> str:
    """Process CSV data and generate insights."""
    code = f"""
# Save the CSV content to a file
with open('{filename}', 'w') as f:
    f.write('''{file_content}''')

# Read and process the CSV
import pandas as pd
df = pd.read_csv('{filename}')

print("Dataset Info:")
print(f"Shape: {{df.shape}}")
print(f"Columns: {{list(df.columns)}}")
print("\\nFirst 5 rows:")
print(df.head())

print("\\nBasic Statistics:")
print(df.describe())

# Check for missing values
print("\\nMissing Values:")
print(df.isnull().sum())

# Save processed data
df_processed = df.fillna(df.mean(numeric_only=True))
df_processed.to_csv('processed_' + '{filename}', index=False)
print(f"\\nProcessed data saved to processed_{{'{filename}'}}")
"""
    
    with code_session("us-west-2") as code_client:
        response = code_client.invoke("executeCode", {
            "code": code,
            "language": "python",
            "clearContext": False
        })
        
        return extract_result(response)
```

### Machine Learning
```python
@tool
def train_simple_model(dataset_description: str) -> str:
    """Train a simple machine learning model."""
    code = f"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# {dataset_description}
# Generate sample data for demonstration
np.random.seed(42)
X = np.random.randn(100, 2)
y = 3 * X[:, 0] + 2 * X[:, 1] + np.random.randn(100) * 0.1

# Create DataFrame
df = pd.DataFrame(X, columns=['feature1', 'feature2'])
df['target'] = y

print("Dataset created:")
print(df.head())

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    df[['feature1', 'feature2']], df['target'], 
    test_size=0.2, random_state=42
)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"\\nModel Performance:")
print(f"Mean Squared Error: {{mse:.4f}}")
print(f"R² Score: {{r2:.4f}}")
print(f"Model Coefficients: {{model.coef_}}")
print(f"Model Intercept: {{model.intercept_:.4f}}")

# Visualize results
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.scatter(y_test, y_pred, alpha=0.7)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.title('Actual vs Predicted')

plt.subplot(1, 2, 2)
residuals = y_test - y_pred
plt.scatter(y_pred, residuals, alpha=0.7)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted')
plt.ylabel('Residuals')
plt.title('Residual Plot')

plt.tight_layout()
plt.savefig('model_evaluation.png')
plt.show()
"""
    
    with code_session("us-west-2") as code_client:
        response = code_client.invoke("executeCode", {
            "code": code,
            "language": "python",
            "clearContext": False
        })
        
        return extract_result(response)
```

## Session Management

### Persistent Sessions
```python
from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreterSession

class PersistentCodeSession:
    def __init__(self, region: str):
        self.region = region
        self.session = None
    
    def start_session(self):
        """Start a persistent code session."""
        self.session = CodeInterpreterSession(self.region)
        return self.session
    
    def execute_code(self, code: str, language: str = "python"):
        """Execute code in the persistent session."""
        if not self.session:
            self.start_session()
        
        return self.session.invoke("executeCode", {
            "code": code,
            "language": language,
            "clearContext": False
        })
    
    def clear_context(self):
        """Clear the session context."""
        if self.session:
            self.session.invoke("clearContext", {})
    
    def close_session(self):
        """Close the session."""
        if self.session:
            self.session.close()
            self.session = None

# Usage
code_session = PersistentCodeSession("us-west-2")

@tool
def execute_in_session(code: str) -> str:
    """Execute code in a persistent session."""
    response = code_session.execute_code(code)
    return extract_result(response)
```

### Multi-step Computations
```python
@tool
def multi_step_analysis(step: int, code: str) -> str:
    """Perform multi-step analysis maintaining context."""
    step_descriptions = {
        1: "Step 1: Data Loading and Exploration",
        2: "Step 2: Data Cleaning and Preprocessing", 
        3: "Step 3: Analysis and Visualization",
        4: "Step 4: Results and Conclusions"
    }
    
    full_code = f"""
# {step_descriptions.get(step, f"Step {step}")}
{code}

# Save current state
import pickle
import os

# Create a state directory if it doesn't exist
os.makedirs('analysis_state', exist_ok=True)

# Save variables to maintain state
state_file = f'analysis_state/step_{step}.pkl'
current_vars = {{k: v for k, v in locals().items() 
                if not k.startswith('_') and k not in ['pickle', 'os']}}

with open(state_file, 'wb') as f:
    pickle.dump(current_vars, f)

print(f"Step {step} completed. State saved.")
"""
    
    with code_session("us-west-2") as code_client:
        response = code_client.invoke("executeCode", {
            "code": full_code,
            "language": "python",
            "clearContext": False
        })
        
        return extract_result(response)
```

## Security and Best Practices

### Code Validation
```python
import ast
import re

def validate_python_code(code: str) -> tuple[bool, str]:
    """Validate Python code for security."""
    # Check for dangerous imports
    dangerous_imports = ['os', 'subprocess', 'sys', 'socket', 'urllib']
    
    for dangerous in dangerous_imports:
        if re.search(rf'\b{dangerous}\b', code):
            return False, f"Dangerous import detected: {dangerous}"
    
    # Check for dangerous functions
    dangerous_functions = ['exec', 'eval', 'open', '__import__']
    
    for dangerous in dangerous_functions:
        if dangerous in code:
            return False, f"Dangerous function detected: {dangerous}"
    
    # Try to parse the code
    try:
        ast.parse(code)
        return True, "Code is valid"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

@tool
def safe_execute_python(code: str, description: str = "") -> str:
    """Execute Python code with safety validation."""
    is_valid, message = validate_python_code(code)
    
    if not is_valid:
        return f"Code validation failed: {message}"
    
    return execute_python(code, description)
```

### Resource Limits
```python
@tool
def execute_with_limits(code: str, timeout: int = 30) -> str:
    """Execute code with resource limits."""
    limited_code = f"""
import signal
import time

def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timed out")

# Set timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm({timeout})

try:
    # Your code here
{code}
finally:
    signal.alarm(0)  # Cancel the alarm
"""
    
    with code_session("us-west-2") as code_client:
        response = code_client.invoke("executeCode", {
            "code": limited_code,
            "language": "python",
            "clearContext": False
        })
        
        return extract_result(response)
```

## Helper Functions

```python
def extract_result(response_stream) -> str:
    """Extract result from code execution response stream."""
    result = ""
    for event in response_stream.get("stream", []):
        if "result" in event:
            result += str(event["result"])
        elif "error" in event:
            result += f"Error: {event['error']}"
    return result

def format_code_output(output: str) -> str:
    """Format code execution output for better readability."""
    lines = output.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip():
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)
```

## Integration with Agent

```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent()

# Add code interpreter tools
agent.add_tool(execute_python)
agent.add_tool(analyze_data)
agent.add_tool(train_simple_model)
agent.add_tool(safe_execute_python)

@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt")
    result = agent(user_message)
    return {"result": result.message}
```

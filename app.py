from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ECS Flask App</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
                max-width: 700px; 
                margin: 40px auto; 
                padding: 20px; 
                color: #333;
                line-height: 1.6;
            }
            .card {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
            }
            hr {
                border: 0;
                border-top: 1px solid #eee;
                margin: 30px 0;
            }
        </style>
    </head>
    <body>
        <h1>🚀 Hello from AWS ECS!</h1>
        <p>This Flask application is successfully running in a Docker container on AWS Elastic Container Service.</p>
        
        <div class="card">
            <h2>Deployment Details</h2>
            <ul>
                <li><strong>Infrastructure:</strong> Provisioned via Terraform</li>
                <li><strong>CI/CD:</strong> Deployed using GitHub Actions</li>
                <li><strong>Container Orchestration:</strong> AWS ECS</li>
            </ul>
        </div>
        
        <hr>
        <p style="color: #28a745; font-weight: bold;">✓ Your CI/CD pipeline is working perfectly.</p>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    # Bind to 0.0.0.0 to allow the AWS Load Balancer to route traffic to it
    app.run(host='0.0.0.0', port=5000)

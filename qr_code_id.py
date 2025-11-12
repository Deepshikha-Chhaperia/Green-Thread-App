from http.server import BaseHTTPRequestHandler
from sqlite3 import connect
from os.path import join, dirname
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract QR code ID from path
        qr_code_id = self.path.split('/')[-1]
        
        # Connect to database
        db_path = join(dirname(__file__), '../../greenthreads.db')
        conn = connect(db_path)
        conn.row_factory = lambda cursor, row: {
            col[0]: row[idx] for idx, col in enumerate(cursor.description)
        }
        
        try:
            # Get care instructions
            cursor = conn.cursor()
            design = cursor.execute("""
                SELECT care_instructions, materials, clothing_type, style
                FROM designs 
                WHERE qr_code_id = ?
            """, (qr_code_id,)).fetchone()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            if design:
                # Create HTML response with styling
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Sustainable Fashion Care Instructions</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            margin: 0;
                            padding: 20px;
                            background: linear-gradient(135deg, #FEFEFA 0%, #FFF8DC 100%);
                        }}
                        .container {{
                            max-width: 800px;
                            margin: 0 auto;
                            background: white;
                            padding: 20px;
                            border-radius: 10px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }}
                        h1 {{
                            color: #8B4513;
                            text-align: center;
                            border-bottom: 2px solid #DAA520;
                            padding-bottom: 10px;
                        }}
                        h2 {{
                            color: #8B4513;
                            margin-top: 20px;
                        }}
                        .details {{
                            margin-bottom: 20px;
                            padding: 15px;
                            background: #FFF8DC;
                            border-radius: 5px;
                        }}
                        .care-instructions {{
                            white-space: pre-line;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Sustainable Fashion Care Guide</h1>
                        <div class="details">
                            <h2>Garment Details</h2>
                            <p><strong>Style:</strong> {design['style']}</p>
                            <p><strong>Type:</strong> {design['clothing_type']}</p>
                            <p><strong>Materials:</strong> {design['materials']}</p>
                        </div>
                        <div class="care-instructions">
                            <h2>Care & Sustainability Instructions</h2>
                            {design['care_instructions']}
                        </div>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html_content.encode())
            else:
                self.wfile.write(b"Care instructions not found")
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(e).encode())
            
        finally:
            conn.close()
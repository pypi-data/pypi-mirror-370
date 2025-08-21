import json
from typing import Dict, Any
import os
from jinja2 import Environment, FileSystemLoader, BaseLoader, Template

# Modern HTML template using Tailwind CSS for a clean, professional design.
HTML_TEMPLATE_STR = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dataset Validation Report</title>
    <!-- Tailwind CSS via CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Fonts: Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Applying the Inter font to the body */
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
    </style>
</head>
<body class="bg-slate-50 text-slate-800">
    <div class="container mx-auto p-4 sm:p-6 lg:p-8">
        <div class="bg-white rounded-2xl shadow-lg overflow-hidden border border-slate-200">
            <!-- Header Section -->
            <header class="bg-slate-800 p-6 sm:p-8">
                <div class="flex items-center justify-between">
                    <div>
                        <h1 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">Dataset Validation Report</h1>
                        <p class="mt-2 text-sm text-slate-300">Comprehensive analysis of data quality and integrity.</p>
                    </div>
                    <div class="flex-shrink-0">
                        <div class="w-12 h-12 bg-slate-700 rounded-lg flex items-center justify-center">
                            <!-- Heroicon: document-check -->
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7 text-indigo-400">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                            </svg>
                        </div>
                    </div>
                </div>
            </header>

            <!-- Main Content -->
            <main class="p-6 sm:p-8 space-y-8">

                <!-- Summary Section -->
                <section>
                    <h2 class="text-xl font-semibold text-slate-900 border-b border-slate-200 pb-3">Summary</h2>
                    <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                        <div class="bg-slate-50 border border-slate-200 rounded-xl p-5">
                            <p class="text-sm font-medium text-slate-500">Total Rows</p>
                            <p class="mt-1 text-3xl font-bold text-indigo-600">{{ summary.total_rows }}</p>
                        </div>
                        <div class="bg-slate-50 border border-slate-200 rounded-xl p-5">
                            <p class="text-sm font-medium text-slate-500">Total Columns</p>
                            <p class="mt-1 text-3xl font-bold text-indigo-600">{{ summary.total_columns }}</p>
                        </div>
                    </div>
                </section>

                <!-- Duplicate Rows Section -->
                <section>
                    <h2 class="text-xl font-semibold text-slate-900 border-b border-slate-200 pb-3">Duplicate Rows</h2>
                    <div class="mt-4">
                        {% if duplicate_rows.count > 0 %}
                            <div class="flex items-center gap-3 bg-red-50 text-red-800 p-4 rounded-lg border border-red-200">
                                <!-- Heroicon: exclamation-triangle -->
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 flex-shrink-0">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                                </svg>
                                <p class="font-medium">Found <span class="font-bold">{{ duplicate_rows.count }}</span> duplicate rows.</p>
                            </div>
                        {% else %}
                            <div class="flex items-center gap-3 bg-green-50 text-green-800 p-4 rounded-lg border border-green-200">
                                <!-- Heroicon: check-circle -->
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 flex-shrink-0">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                </svg>
                                <p class="font-medium">No duplicate rows found.</p>
                            </div>
                        {% endif %}
                    </div>
                </section>

                <!-- Missing Values Section -->
                <section>
                    <h2 class="text-xl font-semibold text-slate-900 border-b border-slate-200 pb-3">Missing Values</h2>
                    <div class="mt-4">
                        {% if missing_values %}
                            <div class="overflow-x-auto border border-slate-200 rounded-lg">
                                <table class="min-w-full divide-y divide-slate-200 text-sm">
                                    <thead class="bg-slate-50">
                                        <tr>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Column</th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Missing Count</th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Missing Percentage</th>
                                        </tr>
                                    </thead>
                                    <tbody class="bg-white divide-y divide-slate-200">
                                        {% for col, details in missing_values.items() %}
                                        <tr>
                                            <td class="px-6 py-4 whitespace-nowrap font-medium text-slate-800">{{ col }}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-slate-600">{{ details.count }}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-slate-600">
                                                <div class="flex items-center gap-3">
                                                    <span>{{ details.percentage }}%</span>
                                                    {% if details.percentage > 50 %}
                                                        <span class="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800">Critical</span>
                                                    {% elif details.percentage > 20 %}
                                                        <span class="inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">High</span>
                                                    {% endif %}
                                                </div>
                                            </td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% else %}
                            <div class="flex items-center gap-3 bg-green-50 text-green-800 p-4 rounded-lg border border-green-200">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 flex-shrink-0">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                </svg>
                                <p class="font-medium">No missing values found.</p>
                            </div>
                        {% endif %}
                    </div>
                </section>
                
                <!-- Outliers Section -->
                <section>
                    <h2 class="text-xl font-semibold text-slate-900 border-b border-slate-200 pb-3">Outliers (IQR Method)</h2>
                     <div class="mt-4">
                        {% if outliers %}
                            <div class="overflow-x-auto border border-slate-200 rounded-lg">
                                <table class="min-w-full divide-y divide-slate-200 text-sm">
                                    <thead class="bg-slate-50">
                                        <tr>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Column</th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Outlier Count</th>
                                        </tr>
                                    </thead>
                                    <tbody class="bg-white divide-y divide-slate-200">
                                        {% for col, details in outliers.items() %}
                                        <tr>
                                            <td class="px-6 py-4 whitespace-nowrap font-medium text-slate-800">{{ col }}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-slate-600">
                                                <div class="flex items-center gap-3">
                                                    <span>{{ details.count }}</span>
                                                    {% if details.count > 100 %}
                                                        <span class="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800">High</span>
                                                    {% elif details.count > 20 %}
                                                        <span class="inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">Medium</span>
                                                    {% endif %}
                                                </div>
                                            </td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% else %}
                             <div class="flex items-center gap-3 bg-green-50 text-green-800 p-4 rounded-lg border border-green-200">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 flex-shrink-0">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                </svg>
                                <p class="font-medium">No outliers detected.</p>
                            </div>
                        {% endif %}
                    </div>
                </section>

                <!-- Categorical Anomalies Section -->
                <section>
                    <h2 class="text-xl font-semibold text-slate-900 border-b border-slate-200 pb-3">Categorical Anomalies</h2>
                    <div class="mt-4 space-y-4">
                        {% if categorical_anomalies %}
                            {% for col, anomalies in categorical_anomalies.items() %}
                                <div>
                                    <h4 class="font-semibold text-slate-700">Column: <span class="font-bold text-indigo-600">{{ col }}</span></h4>
                                    <p class="text-sm text-slate-600 mt-1">Found <span class="font-semibold">{{ anomalies|length }}</span> potential anomalies (rare categories):</p>
                                    <pre class="mt-2 bg-slate-800 text-slate-200 p-4 rounded-lg text-xs overflow-x-auto"><code>{{ anomalies|join(', ') }}</code></pre>
                                </div>
                            {% endfor %}
                        {% else %}
                            <div class="flex items-center gap-3 bg-green-50 text-green-800 p-4 rounded-lg border border-green-200">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 flex-shrink-0">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                </svg>
                                <p class="font-medium">No categorical anomalies found.</p>
                            </div>
                        {% endif %}
                    </div>
                </section>

                <!-- Data Types Section -->
                <section>
                    <h2 class="text-xl font-semibold text-slate-900 border-b border-slate-200 pb-3">Data Types</h2>
                    <div class="mt-4">
                        <div class="overflow-x-auto border border-slate-200 rounded-lg">
                            <table class="min-w-full divide-y divide-slate-200 text-sm">
                                <thead class="bg-slate-50">
                                    <tr>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Column</th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Detected Type</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-slate-200">
                                    {% for col, dtype in data_types.items() %}
                                    <tr>
                                        <td class="px-6 py-4 whitespace-nowrap font-medium text-slate-800">{{ col }}</td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <span class="inline-flex items-center rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700 ring-1 ring-inset ring-slate-200">{{ dtype }}</span>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </section>
            </main>

            <!-- Footer -->
            <footer class="bg-slate-50 border-t border-slate-200 px-6 sm:px-8 py-5 text-center text-sm text-slate-500">
                <p><strong>Developed by Aditya Dinesh, Aydie's Avenue</strong></p>
                <div class="mt-3 space-y-2">
                    <div>
                        <a href="mailto:developer@aydie.in" class="text-indigo-600 hover:text-indigo-800 hover:underline">Contact</a>: <span>developer@aydie.in</span>
                    </div>
                    <div>
                        <a href="www.aydie.in" target="_blank" class="text-indigo-600 hover:text-indigo-800 hover:underline">Website</a>: <span>https://aydie.in</span>
                    </div>
                     <div>
                        <span>Download latest version: </span><a href="https://opensource.aydie.in" target="_blank" class="text-indigo-600 hover:text-indigo-800 hover:underline">opensource.aydie.in</a>
                    </div>
                </div>
            </footer>
        </div>
    </div>
</body>
</html>
"""

class ReportGenerator:
    """
    Generates reports from dataset validation results.

    This class can produce reports in various formats, such as JSON and HTML,
    to provide a human-readable summary of data quality checks.
    """

    def __init__(self, validation_results: Dict[str, Any]):
        """
        Initializes the ReportGenerator with validation results.

        Args:
            validation_results (Dict[str, Any]): The dictionary of results
                from a DatasetValidator instance.
        """
        self.results = validation_results

    def to_json(self, output_path: str, indent: int = 4) -> None:
        """
        Saves the validation results as a JSON file.

        Args:
            output_path (str): The path to save the JSON file (e.g., 'report.json').
            indent (int): The indentation level for pretty-printing the JSON.
                          Defaults to 4.
        """
        print(f"Generating JSON report at: {output_path}")
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=indent)
        print("JSON report generated successfully.")

    def to_html(self, output_path: str) -> None:
        """
        Generates and saves a styled HTML report from the validation results.

        Args:
            output_path (str): The path to save the HTML file (e.g., 'report.html').
        """
        print(f"Generating HTML report at: {output_path}")
        
        # Use the template string directly
        template = Template(HTML_TEMPLATE_STR)
        
        # Render the template with the validation results
        html_content = template.render(self.results)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("HTML report generated successfully.")
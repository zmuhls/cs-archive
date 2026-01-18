---
layout: none
title: Archive Map
description: Interactive map of NYSTA meetings and county consolidation records
permalink: /map/
---
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Common School Archive — Location Map</title>

        <!-- CSS imports -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.8.0/dist/leaflet.css" integrity="sha512-hoalWLoI8r4UszCkZ5kL8vayOGVae1oxXe/2A4AO6J9+580uKHDO3JdHb7NzwwzK5xr/Fs0W40kiNHxM9vyTtQ==" crossorigin=""/>
        <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Inconsolata">

        <style>
            /* Global Styles */
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                font-family: "Inconsolata", sans-serif;
                background-color: #1a1a1a;
                color: #f5f5f5;
            }

            /* Map Container */
            #map {
                width: 100%;
                height: 60vh;
                min-height: 400px;
                margin-top: 50px;
                z-index: 1;
            }

            /* Section Container */
            .sidebar-section {
                padding: 30px 20px;
                max-width: 1400px;
                margin: 0 auto;
                background-color: #2a2a2a;
            }

            .sidebar-section h4 {
                margin-top: 0;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #444;
                color: #f5f5f5;
                font-size: 1.5rem;
            }

            /* Legend Styles */
            .legend {
                background: white;
                padding: 12px;
                border-radius: 5px;
                box-shadow: 0 0 15px rgba(0,0,0,0.3);
                line-height: 1.8;
                color: #333 !important;
            }
            .legend div {
                color: #333 !important;
            }
            .legend i {
                width: 18px;
                height: 18px;
                float: left;
                margin-right: 8px;
                opacity: 0.8;
                border-radius: 50%;
            }
            .legend-title {
                font-weight: bold;
                margin-bottom: 8px;
                color: #333 !important;
            }

            /* Location List Styles */
            .location-list {
                list-style: none;
                padding: 0;
                columns: 2;
                column-gap: 20px;
            }
            .location-list li {
                padding: 8px 12px;
                cursor: pointer;
                border-radius: 3px;
                transition: background-color 0.2s;
                break-inside: avoid;
            }
            .location-list li:hover {
                background: #3a3a3a;
            }

            /* Marker Styles */
            .nysta-marker {
                background: #e74c3c;
            }
            .county-marker {
                background: #3498db;
            }

            /* Tab Styles */
            .tab-container {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 20px;
            }
            .tab {
                padding: 12px 24px;
                cursor: pointer;
                border: none;
                background: #3a3a3a;
                color: #f5f5f5;
                font-family: inherit;
                font-size: 14px;
                border-radius: 3px;
                transition: background-color 0.2s;
            }
            .tab:hover {
                background: #4a4a4a;
            }
            .tab.active {
                background: #555;
                color: white;
                font-weight: bold;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            .tab-content p {
                margin-bottom: 15px;
                color: #ccc;
            }

            /* Navigation */
            .w3-top {
                z-index: 1000;
            }
            .w3-button {
                transition: background-color 0.2s;
            }
            .w3-button:hover {
                background-color: #333 !important;
            }

            /* Footer */
            footer {
                margin-top: 40px;
                background-color: #1a1a1a;
                border-top: 1px solid #333;
            }
            footer p {
                margin: 10px 0;
            }
            footer a {
                color: #3498db;
                text-decoration: none;
                transition: color 0.2s;
            }
            footer a:hover {
                color: #5dade2;
                text-decoration: underline;
            }

            /* Responsive Layout */
            @media (min-width: 768px) {
                #map {
                    height: 70vh;
                }
            }

            @media (max-width: 767px) {
                .sidebar-section {
                    padding: 20px 10px;
                }
                .location-list {
                    columns: 1 !important;
                }
            }
        </style>

        <!-- JS imports -->
        <script src="https://unpkg.com/leaflet@1.8.0/dist/leaflet.js" integrity="sha512-BB3hKbKWOc9Ez/TAwyWxNXeoV9c1v6FIeYiBieIWkpLjauysF18NzgR1MBNBXf8/KABdlkX68nAhlwcDFLGPCQ==" crossorigin=""></script>
    </head>
    <body>
        <div class="w3-top">
            <div class="w3-row w3-padding w3-black">
                <div class="w3-col s3">
                    <a href="/cs-archive/" class="w3-button w3-block w3-black">HOME</a>
                </div>
                <div class="w3-col s3">
                    <a href="/cs-archive/about/" class="w3-button w3-block w3-black">ABOUT</a>
                </div>
                <div class="w3-col s3">
                    <a href="/cs-archive/map/" class="w3-button w3-block w3-black">MAP</a>
                </div>
                <div class="w3-col s3">
                    <a href="https://github.com/zmuhls/cs-archive" class="w3-button w3-block w3-black">REPO</a>
                </div>
            </div>
        </div>

        <div id="map"></div>

        <div class="sidebar-section">
            <h4>Common School Archive — Locations</h4>

            <div class="tab-container">
                <button class="tab active" data-tab="nysta">NYSTA Meetings (1881-1927)</button>
                <button class="tab" data-tab="counties">District Consolidation Counties</button>
            </div>

            <div id="nysta" class="tab-content active">
                <p><strong>16 meeting locations</strong> from the NYS Teachers' Association collection (1845-1940s)</p>
                <ul class="location-list" id="nysta-list"></ul>
            </div>

            <div id="counties" class="tab-content">
                <p><strong>29 counties</strong> with school district consolidation records from NYS Archives Series A4456</p>
                <ul class="location-list" id="county-list"></ul>
            </div>
        </div>

        <!-- Footer -->
        <footer class="w3-center w3-padding-48 w3-large">
            <p style="color: #ccc;">Common School Archive — Digital Humanities Project</p>
            <p style="color: #888; font-size: 0.9rem;">
                <a href="https://github.com/zmuhls/cs-archive">View on GitHub</a>
            </p>
        </footer>

        <script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
        <script src="{{ '/assets/maps/archive-map.js' | relative_url }}"></script>
    </body>
</html>

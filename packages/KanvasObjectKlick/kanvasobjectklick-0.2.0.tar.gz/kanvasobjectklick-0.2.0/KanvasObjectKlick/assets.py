# coding: utf-8

import numpy as np


def create_black_image() -> np.ndarray:
    # Create np.ndarray 8x8 with 3 channels (RGB=BGR) fully filled zeros (black image 8x8)
    black_image = np.zeros((8, 8, 3), dtype=np.uint8)
    return black_image


def get_html_mode_a_part_one() -> str:
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; }
        .tooltip {
            position: absolute;
            background: white;
            border: 1px solid black;
            padding: 5px;
            display: none;
        }
        .image-popup {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 10px;
            border: 1px solid black;
            display: none;
        }
        .image-popup img { max-width: 300px; max-height: 300px; }
    </style>
</head>
<body>
    <svg width="800" height="600"></svg>
    <div class="tooltip"></div>
    <div class="image-popup"><img id="popup-img" src="" alt=""><br><button onclick="closePopup()">Закрыть</button></div>
    
    <script>
        const width = 800, height = 600;
        const margin = 50;
        const data = """


def get_html_mode_a_part_two() -> str:
    return """;

        function visualize(data) {
            const svg = d3.select("svg");
            const tooltip = d3.select(".tooltip");
            const popup = d3.select(".image-popup");
            const popupImg = d3.select("#popup-img");

            const xExtent = d3.extent(data, d => d.x);
            const yExtent = d3.extent(data, d => d.y);
            const xScale = d3.scaleLinear().domain(xExtent).range([margin, width - margin]);
            const yScale = d3.scaleLinear().domain(yExtent).range([height - margin, margin]);

            const xAxis = d3.axisBottom(xScale);
            const yAxis = d3.axisLeft(yScale);

            svg.append("g")
                .attr("transform", `translate(0,${height - margin})`)
                .call(xAxis);

            svg.append("g")
                .attr("transform", `translate(${margin},0)`)
                .call(yAxis);

            svg.selectAll("circle")
                .data(data)
                .enter().append("circle")
                .attr("cx", d => xScale(d.x))
                .attr("cy", d => yScale(d.y))
                .attr("r", 5)
                .attr("fill", d => `rgb(${d.color[0]},${d.color[1]},${d.color[2]})`)
                .on("mouseover", (event, d) => {
                    tooltip.style("display", "block")
                        .style("left", `${event.pageX + 10}px`)
                        .style("top", `${event.pageY + 10}px`)
                        .text(d.name);
                })
                .on("mouseout", () => tooltip.style("display", "none"))
                .on("click", (event, d) => {
                    popupImg.attr("src", d.image);
                    popup.style("display", "block");
                });
        }

        function closePopup() {
            d3.select(".image-popup").style("display", "none");
        }

        visualize(data);
    </script>
</body>
</html>
"""

def get_html_mode_b_part_one() -> str:
    return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; }
        .tooltip {
            position: absolute;
            background: white;
            border: 1px solid black;
            padding: 5px;
            display: none;
        }
        .image-popup {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 10px;
            border: 1px solid black;
            display: none;
        }
        .image-popup img { max-width: 300px; max-height: 300px; }
    </style>
</head>
<body>
    <svg width="800" height="600"></svg>
    <div class="tooltip"></div>
    <div class="image-popup"><img id="popup-img" src="" alt=""><br><button onclick="closePopup()">Закрыть</button></div>
    
    <script>
        const width = 800, height = 600;
        const margin = 50;

        async function loadData() {
            /* const response = await fetch('data.json');
            const data = await response.json(); */
            const data = """


def get_html_mode_b_part_two() -> str:
    return """;
            visualize(data);
        }

        function visualize(data) {
            const svg = d3.select("svg");
            const tooltip = d3.select(".tooltip");
            const popup = d3.select(".image-popup");
            const popupImg = d3.select("#popup-img");

            const xExtent = d3.extent(data, d => d.x);
            const yExtent = d3.extent(data, d => d.y);
            const xScale = d3.scaleLinear().domain(xExtent).range([margin, width - margin]);
            const yScale = d3.scaleLinear().domain(yExtent).range([height - margin, margin]);

            const xAxis = d3.axisBottom(xScale);
            const yAxis = d3.axisLeft(yScale);

            svg.append("g")
                .attr("transform", `translate(0,${height - margin})`)
                .call(xAxis);

            svg.append("g")
                .attr("transform", `translate(${margin},0)`)
                .call(yAxis);

            svg.selectAll("circle")
                .data(data)
                .enter().append("circle")
                .attr("cx", d => xScale(d.x))
                .attr("cy", d => yScale(d.y))
                .attr("r", 5)
                .attr("fill", d => `rgb(${d.color[0]},${d.color[1]},${d.color[2]})`)
                .on("mouseover", (event, d) => {
                    tooltip.style("display", "block")
                        .style("left", `${event.pageX + 10}px`)
                        .style("top", `${event.pageY + 10}px`)
                        .text(d.name);
                })
                .on("mouseout", () => tooltip.style("display", "none"))
                .on("click", (event, d) => {
                    popupImg.attr("src", d.image);
                    popup.style("display", "block");
                });
        }

        function closePopup() {
            d3.select(".image-popup").style("display", "none");
        }

        loadData();
    </script>
</body>
</html>
"""

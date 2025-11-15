#!/usr/bin/env python3
"""
QUANTUM SVG GALERIE MODUL - Advanced Visualizations & Charts
SVG-basierte Charts und Diagramme für das QUANTUM System
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from math import sin, cos, pi

class QuantumSvgGaleriesModul:
    """QUANTUM SVG Galerie für advanced Visualisierungen"""

    def __init__(self):
        self.galerie_themes = self._initialize_themes()
        self.chart_templates = self._initialize_templates()
        self.generated_svgs = []

        print("[QUANTUM SVG GALERIE] Quantum SVG Gallery initialized")
        print("[QUANTUM SVG GALERIE] Themes Available: {}".format(len(self.galerie_themes)))
        print("[QUANTUM SVG GALERIE] Chart Templates: {}".format(len(self.chart_templates)))

    def _initialize_themes(self) -> Dict[str, Any]:
        """Initialize SVG Themes"""
        themes = {
            'quantum_dark': {
                'background': '#0a0a0a',
                'primary': '#00ffff',
                'secondary': '#ff0080',
                'accent': '#ffff00',
                'text': '#ffffff',
                'grid': '#333333',
                'font_family': 'Quantum Sans',
                'glow_effect': True
            },
            'profit_charts': {
                'background': '#001122',
                'primary': '#00ff88',
                'secondary': '#ff4444',
                'accent': '#ffff00',
                'text': '#ffffff',
                'grid': '#223344',
                'font_family': 'Finance Bold',
                'glow_effect': True
            },
            'performance_metrics': {
                'background': '#111111',
                'primary': '#0088ff',
                'secondary': '#ff8800',
                'accent': '#ff00ff',
                'text': '#cccccc',
                'grid': '#444444',
                'font_family': 'Metrics Mono',
                'glow_effect': False
            }
        }
        return themes

    def _initialize_templates(self) -> Dict[str, Any]:
        """Initialize Chart Templates"""
        templates = {
            'profit_chart': {
                'width': 800,
                'height': 400,
                'margins': {'top': 40, 'right': 60, 'bottom': 60, 'left': 80},
                'chart_type': 'line_area'
            },
            'kpi_gauge': {
                'width': 300,
                'height': 300,
                'radius': 120,
                'chart_type': 'circular_gauge'
            },
            'trend_analysis': {
                'width': 1000,
                'height': 500,
                'margins': {'top': 50, 'right': 80, 'bottom': 80, 'left': 100},
                'chart_type': 'bar_line_combo'
            },
            'system_health': {
                'width': 600,
                'height': 400,
                'chart_type': 'donut_chart'
            }
        }
        return templates

    def generate_profit_chart_svg(self, data_points: List[Dict[str, Any]],
                                theme: str = 'profit_charts') -> str:
        """Generiere Profit Chart als SVG"""
        template = self.chart_templates['profit_chart'].copy()
        theme_colors = self.galerie_themes.get(theme, self.galerie_themes['quantum_dark'])

        # Calculate dimensions
        chart_width = template['width'] - template['margins']['left'] - template['margins']['right']
        chart_height = template['height'] - template['margins']['top'] - template['margins']['bottom']

        # Find data range
        if data_points:
            profits = [point.get('profit', 0) for point in data_points]
            min_profit, max_profit = min(profits), max(profits)
        else:
            min_profit, max_profit = 0, 100

        # Generate SVG
        svg_lines = []
        svg_lines.append('<svg width="{}" height="{}" xmlns="http://www.w3.org/2000/svg">'.format(
            template['width'], template['height']))

        # Background
        svg_lines.append('<rect width="100%" height="100%" fill="{}"/>'.format(theme_colors['background']))

        # Add glow effect if enabled
        if theme_colors['glow_effect']:
            svg_lines.append('<defs>')
            svg_lines.append('<filter id="glow">')
            svg_lines.append('<feGaussianBlur stdDeviation="3" result="coloredBlur"/>')
            svg_lines.append('<feMerge>')
            svg_lines.append('<feMergeNode in="coloredBlur"/>')
            svg_lines.append('<feMergeNode in="SourceGraphic"/>')
            svg_lines.append('</feMerge>')
            svg_lines.append('</filter>')
            svg_lines.append('</defs>')

        # Draw grid
        self._add_grid_lines(svg_lines, template, theme_colors)

        # Draw chart lines
        self._add_profit_lines(svg_lines, data_points, template, chart_width, chart_height,
                              min_profit, max_profit, theme_colors)

        # Add labels and title
        svg_lines.append('<text x="{}" y="30" fill="{}" font-family="{}" font-size="18" font-weight="bold">QUANTUM PROFIT ANALYSIS</text>'.format(
            template['width']//2, theme_colors['text'], theme_colors.get('font_family', 'Arial')))

        svg_lines.append('</svg>')

        svg_content = '\n'.join(svg_lines)

        # Record in gallery
        self.generated_svgs.append({
            'type': 'profit_chart',
            'theme': theme,
            'content': svg_content,
            'timestamp': datetime.now().isoformat(),
            'data_points': len(data_points)
        })

        return svg_content

    def _add_grid_lines(self, svg_lines: List[str], template: Dict[str, Any], theme_colors: Dict[str, Any]):
        """Füge Grid-Linien hinzu"""
        for i in range(0, 11):  # 10 horizontal lines
            y = template['margins']['top'] + (template['height'] - template['margins']['top'] - template['margins']['bottom']) * i // 10
            svg_lines.append('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}" stroke-width="0.5" opacity="0.3"/>'.format(
                template['margins']['left'], y, template['width'] - template['margins']['right'], y, theme_colors['grid']))

    def _add_profit_lines(self, svg_lines: List[str], data_points: List[Dict[str, Any]],
                         template: Dict[str, Any], chart_width: int, chart_height: int,
                         min_profit: float, max_profit: float, theme_colors: Dict[str, Any]):
        """Füge Profit-Linien hinzu"""
        if not data_points:
            return

        profit_range = max_profit - min_profit or 1

        # Generate area path
        path_points = []

        for i, point in enumerate(data_points):
            x = template['margins']['left'] + (chart_width * i) // max(1, len(data_points) - 1)
            y = template['margins']['top'] + chart_height - ((point.get('profit', 0) - min_profit) / profit_range * chart_height)

            if i == 0:
                path_points.append('M {} {}'.format(x, template['margins']['top'] + chart_height))
                path_points.append('L {} {}'.format(x, y))
            else:
                path_points.append('L {} {}'.format(x, y))

        # Close area
        path_points.append('L {} {}'.format(x, template['margins']['top'] + chart_height))
        path_points.append('Z')

        # Add area fill
        svg_lines.append('<path d="{}" fill="{}" fill-opacity="0.3" filter="{}"/>'.format(
            ' '.join(path_points), theme_colors['primary'],
            'url(#glow)' if theme_colors['glow_effect'] else 'none'))

        # Add line
        line_path = ' '.join(path_points[:-2]).replace('M ', '').replace('L ', 'L ')  # Remove area part
        svg_lines.append('<path d="{}" fill="none" stroke="{}" stroke-width="3" filter="{}"/>'.format(
            'M ' + ' '.join(line_path.split()[1:]), theme_colors['primary'],
            'url(#glow)' if theme_colors['glow_effect'] else 'none'))

    def generate_kpi_gauge_svg(self, kpi_name: str, current_value: float, target_value: float,
                              theme: str = 'performance_metrics') -> str:
        """Generiere KPI Gauge als SVG"""
        template = self.chart_templates['kpi_gauge'].copy()
        theme_colors = self.galerie_themes.get(theme, self.galerie_themes['quantum_dark'])

        center_x = template['width'] // 2
        center_y = template['height'] // 2
        radius = template['radius']

        # Calculate angle based on achievement
        achievement = min(1.0, current_value / target_value) if target_value != 0 else 0
        angle = achievement * 270 - 135  # Semi-circle from -135 to +135 degrees

        svg_lines = []
        svg_lines.append('<svg width="{}" height="{}" xmlns="http://www.w3.org/2000/svg">'.format(
            template['width'], template['height']))

        # Background circle
        svg_lines.append('<circle cx="{}" cy="{}" r="{}" fill="{}" opacity="0.2"/>'.format(
            center_x, center_y, radius, theme_colors['secondary']))

        # Progress arc
        start_angle = -135 * pi / 180
        end_angle = angle * pi / 180

        # Generate arc path
        x1 = center_x + radius * cos(start_angle)
        y1 = center_y + radius * sin(start_angle)
        x2 = center_x + radius * cos(end_angle)
        y2 = center_y + radius * sin(end_angle)

        large_arc = 1 if angle - (-135) > 180 else 0

        arc_path = 'M {} {} A {} {} 0 {} 1 {} {}'.format(x1, y1, radius, radius, large_arc, x2, y2)
        svg_lines.append('<path d="{}" fill="none" stroke="{}" stroke-width="12" filter="{}"/>'.format(
            arc_path, theme_colors['primary'], 'url(#glow)' if theme_colors['glow_effect'] else 'none'))

        # Add value text
        svg_lines.append('<text x="{}" y="{}" text-anchor="middle" fill="{}" font-family="{}" font-size="24" font-weight="bold">{:.1f}</text>'.format(
            center_x, center_y - 20, theme_colors['text'], theme_colors.get('font_family', 'Arial'), current_value))

        svg_lines.append('<text x="{}" y="{}" text-anchor="middle" fill="{}" font-family="{}" font-size="14">/ {:.1f}</text>'.format(
            center_x, center_y + 10, theme_colors['secondary'], theme_colors.get('font_family', 'Arial'), target_value))

        # Add KPI name
        svg_lines.append('<text x="{}" y="{}" text-anchor="middle" fill="{}" font-family="{}" font-size="16" font-weight="bold">{}</text>'.format(
            center_x, center_y + 50, theme_colors['accent'], theme_colors.get('font_family', 'Arial'), kpi_name.replace('_', ' ').upper()))

        svg_lines.append('</svg>')

        svg_content = '\n'.join(svg_lines)

        # Record in gallery
        self.generated_svgs.append({
            'type': 'kpi_gauge',
            'theme': theme,
            'content': svg_content,
            'timestamp': datetime.now().isoformat(),
            'kpi_name': kpi_name,
            'current_value': current_value,
            'target_value': target_value,
            'achievement': achievement
        })

        return svg_content

    def generate_system_health_donut_svg(self, system_components: Dict[str, float],
                                       theme: str = 'quantum_dark') -> str:
        """Generiere System Health Donut Chart als SVG"""
        template = self.chart_templates['system_health'].copy()
        theme_colors = self.galerie_themes.get(theme, self.galerie_themes['quantum_dark'])

        center_x = template['width'] // 2
        center_y = template['height'] // 2
        outer_radius = 120
        inner_radius = 80

        # Calculate total
        total_value = sum(system_components.values())

        svg_lines = []
        svg_lines.append('<svg width="{}" height="{}" xmlns="http://www.w3.org/2000/svg">'.format(
            template['width'], template['height']))

        # Background
        svg_lines.append('<rect width="100%" height="100%" fill="{}"/>'.format(theme_colors['background']))

        # Generate donut segments
        current_angle = 0
        colors = [theme_colors['primary'], theme_colors['secondary'], theme_colors['accent'],
                 '#ff0080', '#00ffff', '#ffff00']

        for i, (component_name, value) in enumerate(system_components.items()):
            if total_value == 0:
                continue

            segment_angle = (value / total_value) * 360

            # Outer arc
            start_angle = current_angle
            end_angle = current_angle + segment_angle

            # Convert to radians
            start_rad = start_angle * pi / 180
            end_rad = end_angle * pi / 180

            # Calculate points
            x1o = center_x + outer_radius * cos(start_rad)
            y1o = center_y + outer_radius * sin(start_rad)
            x2o = center_x + outer_radius * cos(end_rad)
            y2o = center_y + outer_radius * sin(end_rad)

            x1i = center_x + inner_radius * cos(end_rad)
            y1i = center_y + inner_radius * sin(end_rad)
            x2i = center_x + inner_radius * cos(start_rad)
            y2i = center_y + inner_radius * sin(start_rad)

            large_arc = 1 if segment_angle > 180 else 0

            # Generate donut segment path
            path = 'M {} {} L {} {} A {} {} 0 {} 0 {} {} L {} {} A {} {} 0 {} 1 {} {} Z'.format(
                x1o, y1o, x1i, y1i, inner_radius, inner_radius, large_arc, x2i, y2i,
                x2o, y2o, outer_radius, outer_radius, large_arc, x1o, y1o)

            color = colors[i % len(colors)]
            svg_lines.append('<path d="{}" fill="{}" stroke="{}" stroke-width="2"/>'.format(path, color, theme_colors['background']))

            current_angle += segment_angle

        # Add center text
        svg_lines.append('<text x="{}" y="{}" text-anchor="middle" fill="{}" font-family="{}" font-size="18" font-weight="bold">SYSTEM HEALTH</text>'.format(
            center_x, center_y - 10, theme_colors['text'], theme_colors.get('font_family', 'Arial')))

        svg_lines.append('<text x="{}" y="{}" text-anchor="middle" fill="{}" font-family="{}" font-size="14">{:.1f}%</text>'.format(
            center_x, center_y + 15, theme_colors['accent'], theme_colors.get('font_family', 'Arial'),
            (sum(component for component in system_components.values() if component >= 95) / len(system_components) * 100) if system_components else 0))

        svg_lines.append('</svg>')

        svg_content = '\n'.join(svg_lines)

        # Record in gallery
        self.generated_svgs.append({
            'type': 'system_health_donut',
            'theme': theme,
            'content': svg_content,
            'timestamp': datetime.now().isoformat(),
            'system_components': system_components
        })

        return svg_content

    def get_gallery_preview(self) -> Dict[str, Any]:
        """Hole Gallery Preview"""
        return {
            'total_svgs': len(self.generated_svgs),
            'themes_used': len(set(svg['theme'] for svg in self.generated_svgs)),
            'chart_types': list(set(svg['type'] for svg in self.generated_svgs)),
            'last_generated': self.generated_svgs[-1]['timestamp'] if self.generated_svgs else None,
            'available_themes': list(self.galerie_themes.keys()),
            'available_templates': list(self.chart_templates.keys())
        }

    def export_svg_gallery(self, filename: str = None) -> str:
        """Exportiere gesamte SVG Gallery"""
        if not filename:
            filename = 'quantum_svg_gallery_{}.svg'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))

        # Create combined SVG file
        gallery_content = '<svg width="2000" height="1000" xmlns="http://www.w3.org/2000/svg">\n'

        # Add background
        gallery_content += '<rect width="100%" height="100%" fill="#0a0a0a"/>\n'

        # Add title
        gallery_content += '<text x="1000" y="50" text-anchor="middle" fill="#00ffff" font-size="32" font-weight="bold">QUANTUM SVG GALERIE</text>\n'

        # Add generated SVGs as thumbnails
        for i, svg_data in enumerate(self.generated_svgs[-8:]):  # Show last 8
            row = i // 4
            col = i % 4
            x = 50 + col * 450
            y = 100 + row * 200

            # Add thumbnail border
            gallery_content += '<rect x="{}" y="{}" width="400" height="180" fill="#222222" stroke="#444444" stroke-width="2" rx="10"/>\n'.format(x, y)

            # Add title
            gallery_content += '<text x="{}" y="{}" fill="#ffffff" font-size="14">{}</text>\n'.format(
                x + 10, y + 20, svg_data['type'].replace('_', ' ').upper())

        gallery_content += '</svg>'

        # Save file
        filepath = 'reports/svg_gallery/' + filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(gallery_content)

        return filepath

# Global SVG Gallery Instance
quantum_svg_galerie = QuantumSvgGaleriesModul()

def generate_profit_chart(data_points, theme='profit_charts'):
    """Generiere Profit Chart"""
    return quantum_svg_galerie.generate_profit_chart_svg(data_points, theme)

def generate_kpi_gauge(kpi_name, current_value, target_value, theme='performance_metrics'):
    """Generiere KPI Gauge"""
    return quantum_svg_galerie.generate_kpi_gauge_svg(kpi_name, current_value, target_value, theme)

def generate_system_health_donut(system_components, theme='quantum_dark'):
    """Generiere System Health Donut"""
    return quantum_svg_galerie.generate_system_health_donut_svg(system_components, theme)

def get_svg_gallery_preview():
    """Hole Gallery Preview"""
    return quantum_svg_galerie.get_gallery_preview()

def export_svg_gallery(filename=None):
    """Exportiere SVG Gallery"""
    return quantum_svg_galerie.export_svg_gallery(filename)

if __name__ == "__main__":
    print("QUANTUM SVG GALERIE MODUL - Advanced Visualizations & Charts")
    print("=" * 70)

    print("[QUANTUM SVG GALERIE] Testing Quantum SVG Gallery...")

    # Test Profit Chart
    test_profit_data = [
        {'profit': 125.5},
        {'profit': 234.8},
        {'profit': 189.2},
        {'profit': 312.7},
        {'profit': 267.3}
    ]

    profit_svg = generate_profit_chart(test_profit_data)
    print("[QUANTUM SVG GALERIE] Profit Chart Generated ({} chars)".format(len(profit_svg)))

    # Test KPI Gauge
    kpi_svg = generate_kpi_gauge('System_Performance', 98.5, 99.9)
    print("[QUANTUM SVG GALERIE] KPI Gauge Generated ({} chars)".format(len(kpi_svg)))

    # Test System Health Donut
    health_data = {
        'CPU': 95.2,
        'Memory': 87.5,
        'Disk': 92.1,
        'Network': 96.8
    }

    health_svg = generate_system_health_donut(health_data)
    print("[QUANTUM SVG GALERIE] Health Donut Generated ({} chars)".format(len(health_svg)))

    # Gallery Stats
    preview = get_svg_gallery_preview()
    print("[QUANTUM SVG GALERIE] Gallery Stats: {} SVGs generated in {} themes".format(
        preview['total_svgs'], preview['themes_used']))

    print("\n[QUANTUM SVG GALERIE] QUANTUM SVG VISUALIZATION OPERATIONAL!")
    print("Advanced Charts & Diagrams - Enterprise Visualization System")

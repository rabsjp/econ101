const color_stops = {
    'mono': [
        [255, 255, 255],
        [255, 0, 0]
    ],
    'rainbow': [
        [148, 0, 211],
        [75, 0, 130],
        [0, 0, 255],
        [0, 255, 255],
        [0, 255, 0],
        [255, 255, 0],
        [255, 127, 0],
        [255, 0, 0]
    ]
};

// gets colors from the gradient defined by the color stops above
// 0.0 <= percent <= 1.0
// where percent = 1.0 gets the last color in color_stops and percent = 0.0 gets the first color in color_stops
const get_gradient_color = function(percent, color_scheme) {
    const color = color_stops[color_scheme]
    percent *= (color.length - 1)
    const low_color = Math.floor(percent)
    const high_color = Math.ceil(percent)
    percent -= low_color
    return [0, 1, 2].map(i => percent * color[high_color][i] + (1 - percent) * color[low_color][i])
}

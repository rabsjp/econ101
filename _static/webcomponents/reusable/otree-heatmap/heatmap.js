// function to generate a heatmap for continuous bimatrix
// takes the id of a canvas element and an array of payoffs as arguments

function make_heatmap(canvas_id, payoffs, color_scheme) {
    var canvas = document.getElementById(canvas_id)
    var w = canvas.width
    var h = canvas.height
    var ctx = canvas.getContext('2d')

    var max_payoff = Math.max(payoffs[0], payoffs[1], payoffs[2], payoffs[3])

    // create empty imageData object
    var imageData = ctx.createImageData(w, h)
    var data = imageData.data

    // iterate through every pixel in the image in row major order
    for (var row = 0; row < h; row++) {
        // calculate percent distance from bottom and top of image
        var percent_bottom = row / h
        var percent_top = 1 - percent_bottom
        for (var col = 0; col < w; col++) {
            // calculate percent distance from left and right of image
            var percent_right = col / w
            var percent_left = 1 - percent_right

            // calculate the payoff at each pixel by weighting the payoff at each corner by its distance from the pixel
            point_payoff = (percent_top * percent_left * payoffs[0]) +
                           (percent_top * percent_right * payoffs[1]) +
                           (percent_bottom * percent_left * payoffs[2]) +
                           (percent_bottom * percent_right * payoffs[3])

            // divide the payoff by the max payoff to get an color intensity percentage
            // use get_gradient_color to get the appropriate color in the gradient for that percentage
            point_color = get_gradient_color(point_payoff / max_payoff, color_scheme)

            // set imageData for this pixel to the calculated color
            data[(row * w * 4) + (col * 4)] = point_color[0]
            data[(row * w * 4) + (col * 4) + 1] = point_color[1]
            data[(row * w * 4) + (col * 4) + 2] = point_color[2]
            // set alpha channel to fully opaque
            data[(row * w * 4) + (col * 4) + 3] = 255
        }
    }

    ctx.putImageData(imageData, 0, 0)
}

function make_thermometer(canvas_id, color_scheme) {
    var canvas = document.getElementById(canvas_id);
    var w = canvas.width;
    var h = canvas.height;
    var ctx = canvas.getContext('2d');

    // create empty imageData object
    var imageData = ctx.createImageData(w, h);
    var data = imageData.data;

    for (var row = 0; row < h; row++) {
        point_color = get_gradient_color(1 - (row / h), color_scheme);
        for (var col = 0; col < w; col++) {
            data[(row * w * 4) + (col * 4)] = point_color[0];
            data[(row * w * 4) + (col * 4) + 1] = point_color[1];
            data[(row * w * 4) + (col * 4) + 2] = point_color[2];
            // set alpha channel to fully opaque
            data[(row * w * 4) + (col * 4) + 3] = 255;
        }
    }

    ctx.putImageData(imageData, 0, 0);
}

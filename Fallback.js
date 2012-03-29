// check for CSS animation support
$(document).ready(function () {
    var s = (document.body || document.documentElement).style;
    if (s['animation'] === undefined && s['MozAnimation'] === undefined && s['WebkitAnimation'] === undefined && s['OAnimation'] === undefined && s['msAnimation'] === undefined) {
        // use jQuery to provide the fallback animation
        var offsets = [45.6,13.2,36.2,78,21];
        var speeds = [60,80,70,100,50];
        for (var i = 0;i < 5;i++) {
            var element = $("#background .cloud#cloud" + (i + 1));
            element.animate({left:"100%"},Math.round(offsets[i] * 1000),"linear",(function (element) {
                var cloud = {element:element,speed:Math.round(speeds[i] * 1000)};
                return function () {
                    resetCloud(cloud);
                }
            })(element));
        }
    }
})

function resetCloud(cloud) {
    cloud.element.css("left","-25%");
    cloud.element.animate({left:"100%"},cloud.speed,"linear",function () {
        resetCloud(cloud);
    });
}
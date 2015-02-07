var socket,
	canvas,
	center,
	receivers;

receivers = [];

function init_socket(){
	socket = io.connect('http://' + document.domain + ':' + location.port);
	socket.on('connect', function() {
        socket.emit('connect', {data: 'I\'m connected!'});
    });
    socket.on('draw_data', function(data) {
    	console.log("Center: "+data.pos+", Receivers: "+data.receivers)
    	set_center_pos(data.pos.x,data.pos.y);
    	draw_receivers(data.receivers);
    	canvas.renderAll();
    });
}

function draw_receivers(receiver_data){
	_.forEach(receivers,function(receiver){
		canvas.remove(receiver)
	});
	
	receivers = [];

	_.forEach(receiver_data,function(receiver){
		circle = new fabric.Circle({
			left: (receiver.center.x+200)-receiver.radius,
			top: (receiver.center.y+200)-receiver.radius,
			radius: receiver.radius,
			stroke: 'red',
			fill: 'transparent',
			strokeWidth: 3
		});
		canvas.add(circle);
		receivers.push(circle)
	})
}

function set_center_pos(x,y){
	center.set('left',x+200);
	center.set('top',y+200);
}

$(function(){

	// create a wrapper around native canvas element (with id="c")
	canvas = new fabric.Canvas('main_canvas');
	canvas.setHeight($(window).height());
	canvas.setWidth($(window).width())
	canvas.renderAll();

	init_socket();

	// create a rectangle object
	center = new fabric.Circle({
	  left: 100,
	  top: 100,
	  fill: 'green',
	  radius: 10
	});

	// "add" rectangle onto canvas
	canvas.add(center);
});
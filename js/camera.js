/*
 * Moveable "top-down" camera
 *
 * Shows the map from above and allows moving around with the cursor keys and
 * zooming in/out.
 *
 * Heavily inspired by three.js examples.
 */

Camera = function( parameters ) {
	THREE.Camera.call( this, parameters.fow, parameters.aspect, parameters.near, parameters.far, parameters.target );

	this.movementSpeed = 1.0;
	this.zoom = 40;
	this.minZoom = 8;
	this.domElement = document;
	this.lastUpdate = new Date().getTime();
	this.tdiff = 0;

	if ( parameters ) {
		if ( parameters.movementSpeed !== undefined ) this.movementSpeed = parameters.movementSpeed;
		if ( parameters.zoom !== undefined ) this.zoom = parameters.zoom;
	}

	this.moveLeft = false;
	this.moveRight = false;
	this.moveUp = false;
	this.moveDown = false;
	this.zoomIn = false;
	this.zoomOut = false;

	this.onKeyDown = function( event ) {
		switch( event.keyCode ) {
			case 38: /*up*/
			case 87: /*W*/ this.moveUp = true; break;

			case 37: /*left*/
			case 65: /*A*/ this.moveLeft = true; break;

			case 40: /*down*/
			case 83: /*S*/ this.moveDown = true; break;

			case 39: /*right*/
			case 68: /*D*/ this.moveRight = true; break;

			case 107: /* numpad + */ this.zoomIn = true; break;
			case 109: /* numpad - */ this.zoomOut = true; break;
		}
	};

	this.onKeyUp = function( event ) {
		switch( event.keyCode ) {
			case 38: /*up*/
			case 87: /*W*/ this.moveUp = false; break;

			case 37: /*left*/
			case 65: /*A*/ this.moveLeft = false; break;

			case 40: /*down*/
			case 83: /*S*/ this.moveDown = false; break;

			case 39: /*right*/
			case 68: /*D*/ this.moveRight = false; break;

			case 107: /* numpad + */ this.zoomIn = false; break;
			case 109: /* numpad - */ this.zoomOut = false; break;
		}
	};

	this.update = function() {
		var now = new Date().getTime();
		this.tdiff = ( now - this.lastUpdate ) / 1000;
		this.lastUpdate = now;

		var actualMoveSpeed = this.tdiff * this.movementSpeed;

		if ( this.moveLeft ) this.translateX( -actualMoveSpeed );
		if ( this.moveRight ) this.translateX( actualMoveSpeed );
		if ( this.moveUp ) this.translateY( actualMoveSpeed );
		if ( this.moveDown ) this.translateY( -actualMoveSpeed );
		if ( this.zoomIn && this.zoom > this.minZoom ) this.zoom -= 1;
		if ( this.zoomOut ) this.zoom += 1;

		// The more you zoom out, the faster the camera moves.
		this.movementSpeed = this.zoom * 2;

		this.position.z = this.zoom;

		this.supr.update.call(this);
	};
	
	this.domElement.addEventListener( 'keydown', bind( this, this.onKeyDown ), false );
	this.domElement.addEventListener( 'keyup', bind( this, this.onKeyUp ), false );

	function bind( scope, fn ) {
		return function () {
			fn.apply( scope, arguments );
		};
	};

	this.update();
}

Camera.prototype = new THREE.Camera;
Camera.prototype.constructor = Camera;
Camera.prototype.supr = THREE.Camera.prototype;

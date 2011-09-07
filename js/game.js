/*
 * Parse map data and create geometry.
 */


// To show only part of the big sprite image, we need to adjust the
// texture coordinates on the plane geometry.
function setSpriteTile( geom, coords ) {
	var j, uv = geom.faceVertexUvs[0][0];

	for ( j = 0; j < uv.length; j++ ) {
		if ( uv[j].u === 0 ) {
			uv[j].u = coords[2];
		} else {
			uv[j].u = coords[4];
		}
		if ( uv[j].v === 0 ) {
			uv[j].v = coords[3];
		} else {
			uv[j].v = coords[5];
		}
	}
}


function loadTexture( url ) {
    var texture = THREE.ImageUtils.loadTexture( url, THREE.UVMapping );
    // Linear filtering makes the textures blurry and has its
    // problems on the edges of the texure. Nearest filtering keeps the
	// pixel look intact.
    texture.minFilter = texture.magFilter = THREE.NearestFilter;

    return texture;
}


var Game = {
	scene: null,
	camera: null,
	MAP_DIMENSION: 256,

	init: function() {
		this.scene = new THREE.Scene();
		this.camera = new Camera({
			fov: 60, aspect: window.innerWidth / window.innerHeight, near: 1, far: 20000,
			movementSpeed: 80, zoom: 40
		});

		// Move camera to map's center
		this.camera.translateX( this.MAP_DIMENSION / 2 );
		this.camera.translateY( -this.MAP_DIMENSION / 2 );

		this.loadData();
	},

	loadData: function() {
		this.tiles_texture = loadTexture( "_build/tiles.png" );
		this.tiles_transparent_texture = loadTexture( "_build/tiles_transparent.png" );
		this.sprites_texture = loadTexture( "_build/sprites.png" );

		var requests = $.when(
			this.getData( "block_data", "_build/blocks.json" ),
			this.getData( "map_data", "_build/map.json" ),
			this.getData( "object_pos_data", "_build/object_pos.json" ),
			this.getData( "object_info_data", "_build/object_info.json" ),
			this.getData( "car_info_data", "_build/car_info.json" ),
			this.getData( "sprite_coords_data", "_build/sprites.json" )
		)

		requests.then( $.proxy( this.loadMap, this ) );
	},

	getData: function( name, url ) {
		var self = this;
		return $.getJSON( url ).success(function( data ) {
			self[ name ] = data;
		});
	},

	loadMap: function() {
		this.loadBlocks();
		this.loadMapObjects();
	},

	loadBlocks: function() {
		var solid_geometry = new THREE.Geometry(),
			flat_geometry = new THREE.Geometry();

		for ( var i = 0, count = this.map_data.length; i < count; i++ ) {
			var column = this.map_data[ i ],
				x = i % this.MAP_DIMENSION,
				z = Math.floor( i / this.MAP_DIMENSION );

			for ( var j = 0, block_count = column.length; j < block_count; j++ ) {
				var block = column[ j ],
					data = this.block_data[ block ],
					mesh;

				if ( data[ 7 ] ) {
					mesh = new THREE.Mesh( new FlatBlockGeometry( data ) );
					mesh.position.set( x + 0.5, block_count - j, z + 0.5 );
					THREE.GeometryUtils.merge( flat_geometry, mesh );
				} else {
					mesh = new THREE.Mesh( new SolidBlockGeometry( data ) );
					mesh.position.set( x + 0.5, block_count - j, z + 0.5 );
					THREE.GeometryUtils.merge( solid_geometry, mesh );
				}

		    };
		};

		var mesh = new THREE.Mesh( solid_geometry, new THREE.MeshBasicMaterial({ color: 0xffffff, map: this.tiles_texture }) );
		mesh.rotation.x = 90 * Math.PI / 180;
		mesh.matrixAutoUpdate = false;
		mesh.updateMatrix();
		this.scene.addObject( mesh );

		mesh = new THREE.Mesh( flat_geometry, new THREE.MeshBasicMaterial({ color: 0xffffff, map: this.tiles_transparent_texture, transparent: true }) );
		mesh.rotation.x = 90 * Math.PI / 180;
		mesh.doubleSided = true;
		mesh.matrixAutoUpdate = false;
		mesh.updateMatrix();
		this.scene.addObject( mesh );
	},

	loadMapObjects: function() {
		var geometry = new THREE.Geometry();

		for ( var i = 0, count = this.object_pos_data.length; i < count; i++ ) {
			var object_pos = this.object_pos_data[ i ],
				object_info, sprite_num, coords, mesh, data;

			// Parking cars
			if ( object_pos[ 4 ] ) {
				object_info = this.car_info_data[ object_pos[ 3 ] ];
				if ( object_info === undefined ) {
					continue;
				}
				sprite_num = object_info[ 0 ];
				data = this.sprite_coords_data[ 'car' ];
			// Objects (trash cans, trees, etc.)
			} else {
				object_info = this.object_info_data[ object_pos[ 3 ] ];
				sprite_num = object_info[ 3 ];
				data = this.sprite_coords_data[ 'object' ];
			}

			coords = data[ sprite_num ];
			mesh = new THREE.Mesh( new THREE.PlaneGeometry( coords[0] / 64, coords[1] / 64 ) );

			// Dismiss all other objects with a tire sprite except the real tire object.
			// Disable this, and you will see a lot of tires floating around unusual places.
			// TODO find out why
			if ( sprite_num == 0 && object_pos[ 3 ] != 0 ) {
				continue;
			}

			mesh.position.set( object_pos[ 0 ] / 64, object_pos[ 2 ] / 64 - 1.4, object_pos[ 1 ] / 64 );
			mesh.rotation.x = -90 * Math.PI / 180;
			mesh.rotation.z = object_pos[ 5 ] * Math.PI / 180;
			setSpriteTile( mesh.geometry, coords );

			THREE.GeometryUtils.merge( geometry, mesh );
		};

		var mesh = new THREE.Mesh( geometry, new THREE.MeshBasicMaterial({ color: 0xffffff, map: this.sprites_texture, transparent: true}) );
		mesh.rotation.x = 90 * Math.PI / 180;
		mesh.matrixAutoUpdate = false;
		mesh.updateMatrix();

		this.scene.addObject( mesh );
	}
};

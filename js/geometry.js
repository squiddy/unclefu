function calculateTileUVs( tile, rotation, transparent ) {
	if ( transparent === true ) {
		tile += 384;
	}

	var tiles_per_axis = 32,
		s = tile % tiles_per_axis,
		t = Math.floor( tile / tiles_per_axis ),
		uvs;

	uvs = [
		new THREE.UV(  s      / tiles_per_axis,  t      / tiles_per_axis ),
		new THREE.UV(  s      / tiles_per_axis, (t + 1) / tiles_per_axis ),
		new THREE.UV( (s + 1) / tiles_per_axis, (t + 1) / tiles_per_axis ),
		new THREE.UV( (s + 1) / tiles_per_axis,  t      / tiles_per_axis )
	];

	if ( rotation !== undefined ) {
		for ( var i = 0; i < rotation; i++ ) {
			uvs.push( uvs.shift() );
		}
	}

	return uvs;
}


SolidBlockGeometry = function ( block_data ) {

	THREE.Geometry.call( this );

	var d = 0.5,
		vertices = [
			[ -d, -d, -d ], // 0
			[  d, -d, -d ], // 1
			[ -d ,-d,  d ], // 2
			[  d, -d,  d ], // 3

			[ -d,  d, -d ], // 4
			[  d,  d, -d ], // 5
			[ -d , d,  d ], // 6
			[  d,  d,  d ], // 7
		];

	var slope = block_data[ 8 ];

	// 45 degrees
	if ( slope > 40 && slope < 45 ) {
		if ( slope == 41 ) {
			vertices[ 6 ][ 1 ] = vertices[ 7 ][ 1 ] = -d;
		} else if ( slope == 42 ) {
			vertices[ 4 ][ 1 ] = vertices[ 5 ][ 1 ] = -d;
		} else if ( slope == 43 ) {
			vertices[ 5 ][ 1 ] = vertices[ 7 ][ 1 ] = -d;
		} else if ( slope == 44 ) {
			vertices[ 4 ][ 1 ] = vertices[ 6 ][ 1 ] = -d;
		}
	}

	// 7 degrees
	if ( slope >= 9 && slope < 41 ) {
		if ( slope >= 9 && slope <= 16 ) {
			var part = slope - 9;
			vertices[ 6 ][ 1 ] = vertices[ 7 ][ 1 ] = -d + part / 8;
			vertices[ 4 ][ 1 ] = vertices[ 5 ][ 1 ] = -d + (part + 1)  / 8;
		} else if ( slope >= 17 && slope <= 24 ) {
			var part = slope - 17;
			vertices[ 4 ][ 1 ] = vertices[ 5 ][ 1 ] = -d + part / 8;
			vertices[ 6 ][ 1 ] = vertices[ 7 ][ 1 ] = -d + (part + 1)  / 8;
		} else if ( slope >= 25 && slope <= 32 ) {
			var part = slope - 25;
			vertices[ 5 ][ 1 ] = vertices[ 7 ][ 1 ] = -d + part / 8;
			vertices[ 4 ][ 1 ] = vertices[ 6 ][ 1 ] = -d + (part + 1)  / 8;
		} else if ( slope >= 33 && slope <= 40 ) {
			var part = slope - 33;
			vertices[ 4 ][ 1 ] = vertices[ 6 ][ 1 ] = -d + part / 8;
			vertices[ 5 ][ 1 ] = vertices[ 7 ][ 1 ] = -d + (part + 1)  / 8;
		}

	}

	// 26 degrees
	if ( slope > 0 && slope < 9 ) {
		if ( slope >= 1 && slope <= 2 ) {
			var part = slope - 1;
			vertices[ 6 ][ 1 ] = vertices[ 7 ][ 1 ] = -d + part / 2;
			vertices[ 4 ][ 1 ] = vertices[ 5 ][ 1 ] = -d + (part + 1)  / 2;
		} else if ( slope >= 3 && slope <= 4 ) {
			var part = slope - 3;
			vertices[ 4 ][ 1 ] = vertices[ 5 ][ 1 ] = -d + part / 2;
			vertices[ 6 ][ 1 ] = vertices[ 7 ][ 1 ] = -d + (part + 1)  / 2;
		} else if ( slope >= 5 && slope <= 6 ) {
			var part = slope - 5;
			vertices[ 5 ][ 1 ] = vertices[ 7 ][ 1 ] = -d + part / 2;
			vertices[ 4 ][ 1 ] = vertices[ 6 ][ 1 ] = -d + (part + 1)  / 2;
		} else if ( slope >= 7 && slope <= 8 ) {
			var part = slope - 7;
			vertices[ 4 ][ 1 ] = vertices[ 6 ][ 1 ] = -d + part / 2;
			vertices[ 5 ][ 1 ] = vertices[ 7 ][ 1 ] = -d + (part + 1)  / 2;
		}
	}

	var tiles = {
			nx: block_data[1],
			px: block_data[2],
			nz: block_data[3],
			pz: block_data[4],
			py: block_data[5]
		},
		faces = {
			pz: new THREE.Face4( 6, 2, 3, 7, null, null ),
			px: new THREE.Face4( 7, 3, 1, 5, null, null ),
			nz: new THREE.Face4( 5, 1, 0, 4, null, null ),
			nx: new THREE.Face4( 4, 0, 2, 6, null, null ),
			py: new THREE.Face4( 4, 6, 7, 5, null, null )
		};

	for ( var i = 0; i < vertices.length; i++ ) {
		this.vertices.push( new THREE.Vertex(
			new THREE.Vector3( vertices[i][0], vertices[i][1], vertices[i][2] )
		) );
	}

	for ( var face in faces ) {
		if ( tiles[face] === 0 ) continue;

		this.faces.push( faces[face] );

		var rotation = ( face === 'py' ) ? block_data[ 6 ] : 0;
		var uvs = calculateTileUVs( tiles[face], rotation );

		this.faceVertexUvs[ 0 ].push( uvs );
	}

	this.computeCentroids();
	this.computeFaceNormals();
};

SolidBlockGeometry.prototype = new THREE.Geometry();
SolidBlockGeometry.prototype.constructor = SolidBlockGeometry;


FlatBlockGeometry = function ( block_data ) {

	THREE.Geometry.call( this );

	var d = 0.5,
		vertices = [
			[ -d, -d, -d ], // 0
			[  d, -d, -d ], // 1
			[ -d ,-d,  d ], // 2

			[ -d,  d, -d ], // 3
			[  d,  d, -d ], // 4
			[ -d , d,  d ], // 5
			[  d,  d,  d ], // 6
		];

	var slope = block_data[ 8 ];

	// 45 degrees
	if ( slope > 40 && slope < 45 ) {
		if ( slope == 41 ) {
			vertices[ 6 ][ 1 ] = vertices[ 5 ][ 1 ] = -d;
		} else if ( slope == 42 ) {
			vertices[ 4 ][ 1 ] = vertices[ 3 ][ 1 ] = -d;
		} else if ( slope == 43 ) {
			vertices[ 4 ][ 1 ] = vertices[ 6 ][ 1 ] = -d;
		} else if ( slope == 44 ) {
			vertices[ 3 ][ 1 ] = vertices[ 5 ][ 1 ] = -d;
		}
	}

	// 7 degrees
	if ( slope >= 9 && slope < 41 ) {
		if ( slope >= 9 && slope <= 16 ) {
			var part = slope - 9;
			vertices[ 5 ][ 1 ] = vertices[ 6 ][ 1 ] = -d + part / 8;
			vertices[ 4 ][ 1 ] = vertices[ 3 ][ 1 ] = -d + (part + 1)  / 8;
		} else if ( slope >= 17 && slope <= 24 ) {
			var part = slope - 17;
			vertices[ 4 ][ 1 ] = vertices[ 3 ][ 1 ] = -d + part / 8;
			vertices[ 5 ][ 1 ] = vertices[ 6 ][ 1 ] = -d + (part + 1)  / 8;
		} else if ( slope >= 25 && slope <= 32 ) {
			var part = slope - 25;
			vertices[ 4 ][ 1 ] = vertices[ 6 ][ 1 ] = -d + part / 8;
			vertices[ 3 ][ 1 ] = vertices[ 5 ][ 1 ] = -d + (part + 1)  / 8;
		} else if ( slope >= 33 && slope <= 40 ) {
			var part = slope - 33;
			vertices[ 3 ][ 1 ] = vertices[ 5 ][ 1 ] = -d + part / 8;
			vertices[ 4 ][ 1 ] = vertices[ 6 ][ 1 ] = -d + (part + 1)  / 8;
		}
	}

	// 26 degrees
	if ( slope > 0 && slope < 9 ) {
		if ( slope >= 1 && slope <= 2 ) {
			var part = slope - 1;
			vertices[ 5 ][ 1 ] = vertices[ 6 ][ 1 ] = -d + part / 2;
			vertices[ 4 ][ 1 ] = vertices[ 3 ][ 1 ] = -d + (part + 1)  / 2;
		} else if ( slope >= 3 && slope <= 4 ) {
			var part = slope - 3;
			vertices[ 4 ][ 1 ] = vertices[ 3 ][ 1 ] = -d + part / 2;
			vertices[ 5 ][ 1 ] = vertices[ 6 ][ 1 ] = -d + (part + 1)  / 2;
		} else if ( slope >= 5 && slope <= 6 ) {
			var part = slope - 5;
			vertices[ 4 ][ 1 ] = vertices[ 6 ][ 1 ] = -d + part / 2;
			vertices[ 3 ][ 1 ] = vertices[ 5 ][ 1 ] = -d + (part + 1)  / 2;
		} else if ( slope >= 7 && slope <= 8 ) {
			var part = slope - 7;
			vertices[ 3 ][ 1 ] = vertices[ 5 ][ 1 ] = -d + part / 2;
			vertices[ 4 ][ 1 ] = vertices[ 6 ][ 1 ] = -d + (part + 1)  / 2;
		}
	}

	var tiles = {
			px: block_data[2],
			nz: block_data[3],
			py: block_data[5]
		},
		faces = {
			px: new THREE.Face4( 3, 0, 2, 5, null, null ),
			nz: new THREE.Face4( 4, 1, 0, 3, null, null ),
			py: new THREE.Face4( 3, 5, 6, 4, null, null )
		};

	for ( var i = 0; i < vertices.length; i++ ) {
		this.vertices.push( new THREE.Vertex(
			new THREE.Vector3( vertices[i][0], vertices[i][1], vertices[i][2] )
		) );
	}

	for ( var face in faces ) {
		if ( tiles[face] === 0 ) continue;

		this.faces.push( faces[face] );

		var rotation = ( face === 'py' ) ? block_data[ 6 ] : 0;
		var uvs = calculateTileUVs( tiles[face], rotation, true );

		this.faceVertexUvs[ 0 ].push( uvs );
	}

	this.computeCentroids();
	this.computeFaceNormals();
};

FlatBlockGeometry.prototype = new THREE.Geometry();
FlatBlockGeometry.prototype.constructor = FlatBlockGeometry;

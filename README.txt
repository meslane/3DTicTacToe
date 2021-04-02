DONE List:
-3D projection
-Drawing polygons
-STL file importing
-Back face culling
-Point source lighting and shading
-Painter's algorithm

Click Detection Algorithm:
-iterate through each polygon and get its projection
	-for each projection, determine if the projected polygon contains the point (0,0)
		-if so, the polygon intersects the camera

-of the polygons that intersect the camera, if any are found, determine which is closest to the camera
	-that polygon is the clicked polygon

TODO:
-Add point in polygon detection method
-Fix drawing squares so it doesn 'fold' the polygon
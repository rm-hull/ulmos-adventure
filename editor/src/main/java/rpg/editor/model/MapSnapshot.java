package rpg.editor.model;

import java.util.Map;

import org.eclipse.swt.graphics.Point;

public class MapSnapshot {
	
	private MapTileSnapshot[][] mapTiles;
	
	public MapSnapshot(Map<Point, MapTileSnapshot> tileSnapshots) {
		// work out the size of our array first
		int minX = 127, minY = 127;
		int maxX = 0, maxY = 0;
		for (Point tilePoint: tileSnapshots.keySet()) {
			minX = Math.min(minX, tilePoint.x);
			minY = Math.min(minY, tilePoint.y);
			maxX = Math.max(maxX, tilePoint.x);
			maxY = Math.max(maxY, tilePoint.y);
		}
		int cols = maxX - minX + 1;
		int rows = maxY - minY + 1;
		// and then populate it
		mapTiles = new MapTileSnapshot[cols][rows];
		for (Point tilePoint: tileSnapshots.keySet()) {
	    	int x = tilePoint.x - minX;
	    	int y = tilePoint.y - minY;
	    	mapTiles[x][y] = tileSnapshots.get(tilePoint);
		}
	}

	public MapTileSnapshot[][] getMapTiles() {
		return mapTiles;
	}
	
	public String toString() {
		StringBuffer buffer = new StringBuffer("MapSnapshot [");
		buffer.append("cols: " + mapTiles.length);
		buffer.append(", rows: " + mapTiles[0].length);
		buffer.append("]");
		return buffer.toString();
	}
}

class MapTileSnapshot {
	
	private TileSnapshot[] tiles;
	private String[] levels;
	
	public TileSnapshot[] getTiles() {
		return tiles;
	}
	
	public void setTiles(TileSnapshot[] tiles) {
		this.tiles = tiles;
	}
	
	public String[] getLevels() {
		return levels;
	}
	
	public void setLevels(String[] levels) {
		this.levels = levels;
	}
}

class TileSnapshot {
	
	private String name;
	private String maskLevel;
	
	public String getName() {
		return name;
	}
	
	public void setName(String name) {
		this.name = name;
	}
	
	public String getMaskLevel() {
		return maskLevel;
	}
	
	public void setMaskLevel(String maskLevel) {
		this.maskLevel = maskLevel;
	}
}
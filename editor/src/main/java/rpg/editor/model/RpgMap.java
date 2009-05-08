package rpg.editor.model;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.InputStream;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.graphics.PaletteData;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.widgets.FileDialog;

import rpg.editor.Constants;
import rpg.editor.core.DisplayHelper;
import rpg.editor.core.NewMapDialog;
import rpg.editor.core.SharedTileSelection;
import rpg.editor.core.TileConversion;
import rpg.editor.core.ViewSize;

/**
 * Represents the map data as required by the game engine, including functionality
 * to load/save a map from/to disk.  Users create and edit an instance of this
 * class through the MapEditor component.
 * @author seldred
 */
public class RpgMap {

	private static final String MAPS_PROPERTIES = "maps.properties";

	private static final String MAPS_PATH = "maps.path";
	private static final String MAPS_EXTENSION = "maps.extension";
	
	private static final int TILE_SIZE = ViewSize.MEDIUM.getTileSize();
	
	private static final RGB COLOUR_A = new RGB(204, 153, 204);
	private static final RGB COLOUR_B = new RGB(153, 204, 204);
		
	private static String mapsPath;
	private static String mapsExtension;
	
	private static String[] validExtensions;
	
	private TileConversion tileConversion = SharedTileSelection.getInstance();
	
    private MapTile[][] mapTiles;

	private Point size;
    private String path;
    private Image mapImage;    

	static {
		try {
			InputStream input = ClassLoader.getSystemResourceAsStream(MAPS_PROPERTIES);
			Properties properties = new Properties();
			properties.load(input);
			mapsPath = properties.getProperty(MAPS_PATH);
			if (mapsPath.charAt(mapsPath.length() - 1) != Constants.SLASH) {
				mapsPath = mapsPath + Constants.SLASH;
			}
			mapsExtension = properties.getProperty(MAPS_EXTENSION);
			if (mapsExtension.charAt(0) != Constants.DOT) {
				mapsExtension = Constants.DOT + mapsExtension;
			}
			validExtensions = new String[] { Constants.STAR + mapsExtension };
			logProperties();
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}

	private static void logProperties() {
		System.out.println("maps properties");
		System.out.println("- " + MAPS_PATH + ": " + mapsPath);
		System.out.println("- " + MAPS_EXTENSION + ": " + mapsExtension);
	}
	
    public static RpgMap newRpgMap() {
		NewMapDialog newMapDialog = new NewMapDialog(DisplayHelper.getShell());
		Point size = newMapDialog.getSize();
		if (size != null) {
	    	return new RpgMap(size);			
		}
    	return null;
    }
    
    public static RpgMap loadRpgMap() {
		FileDialog dialog = new FileDialog(DisplayHelper.getShell(), SWT.OPEN);
		dialog.setFilterPath(mapsPath);
		dialog.setFilterExtensions(validExtensions);
		dialog.setText("Open an map file or cancel");
		String mapPath = dialog.open();
		if (mapPath != null) {
			return new RpgMap(mapPath);
		}
		return null;
    }
    
    private RpgMap(Point size) {
    	initialiseMap(size);
	}
    
    private RpgMap(String mapPath) {
    	path = mapPath;
	    Map<Point, String[]> tileData = new HashMap<Point, String[]>();
	    int maxX = 0, maxY = 0;
		BufferedReader reader = null;
		try {
			reader = new BufferedReader(new FileReader(path));
			String lot = null;
			while ((lot = reader.readLine()) != null) {
				lot = lot.trim();
				if (lot.length() > 0) {
					String[] bits = lot.split(Constants.SPACE);
					if (bits.length > 0) {
				    	String[] xny = bits[0].split(Constants.COMMA);
				    	int x = Integer.parseInt(xny[0]), y = Integer.parseInt(xny[1]);
				    	maxX = x > maxX ? x : maxX;
				    	maxY = y > maxY ? y : maxY;
						if (bits.length > 1) {
					    	Point tilePoint = new Point(x, y);
					    	tileData.put(tilePoint, bits);
						}					
					}					
				}
			}
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	    finally {
	    	if (reader != null) {
	    		try {
	    			reader.close();
	    			reader = null;
	    		}
	    		catch (Exception e) { ; }
	    	}
	    }
	    
	    // create map tiles
	    initialiseMap(new Point(++maxX, ++maxY));
	    Map<String, TileSet> tileSets = new HashMap<String, TileSet>();
	    for (Point tilePoint: tileData.keySet()) {
	    	int x = tilePoint.x, y = tilePoint.y;
	    	MapTile mapTile = mapTiles[x][y];
	    	String[] bits = tileData.get(tilePoint);
	    	populateMapTile(mapTile, bits, tileSets);
	    	updateTileImage(mapTile, tilePoint);
	    }
    }
    
    private TileSet getTileSet(String tileSetName, Map<String, TileSet> tileSets) {
   		TileSet tileSet = null;
   		if (tileSets.containsKey(tileSetName)) {
   			tileSet = tileSets.get(tileSetName);
   		}
   		else {
	    	tileSet = TileSet.loadTileSet(tileSetName);
	    	if (tileSet != null) {
	    		tileSets.put(tileSetName, tileSet);
	    	}		    			
   		}
   		return tileSet;
    }
    
    private void populateMapTile(MapTile mapTile, String[] bits, Map<String, TileSet> tileSets) {
    	// we know there's at least one string or we wouldn't have added it
    	// to the map in the first place
    	int startIndex = 1;
    	String firstBit = bits[startIndex].trim();
    	// parse levels
    	if (firstBit.charAt(0) == Constants.OPEN_SQ_BRACKET) {
    		// levels
    		String levels = firstBit.substring(1, firstBit.length() - 1);
    		// System.out.println(levels);
    		mapTile.setLevels(levels.split(Constants.COMMA));
    		startIndex++;
    	}
    	// parse tile images
    	for (int i = startIndex; i < bits.length; i++) {
    		String tileString = bits[i].trim();
    		if (tileString.length() > 0) {
	    		String[] tileBits = tileString.split(Constants.COLON);
	    		if (tileBits.length > 1) {
		    		String tileSetName = tileBits[0];
       	    		TileSet tileSet = getTileSet(tileSetName, tileSets);
       	    		if (tileSet == null) {
       	    			System.out.println("tile set not found: " + tileSetName);
       	    		}
       	    		else {
    		    		Tile tempTile = tileSet.getTile(tileBits[1]);
    		    		if (tempTile != null) {
    			    		Tile tile = tileConversion.convertTile(tempTile);
    			    		if (tileBits.length > 2) {
    			    			// contains a mask level
    			    			try {
    				    			mapTile.addTile(tile, tileBits[2]);
    			    			}
    			    			catch (NumberFormatException e) { ; }
    			    		}
    			    		else {
    				    		mapTile.addTile(tile);		    			
    			    		}		    			
    		    		}       	    			
       	    		}
	    		}
    		}
    	}    	
    }
    
    private void pasteIntoMapTile(MapTile mapTile, MapTileSnapshot snapshot, Map<String, TileSet> tileSets) {
    	mapTile.clearTiles();
    	String[] levels = snapshot.getLevels();
    	if (levels != null) {
       		mapTile.setLevels(snapshot.getLevels());
    	}
    	TileSnapshot[] tiles = snapshot.getTiles();
    	if ((tiles != null) && (tiles.length > 0)) {
       		for (TileSnapshot tileSnapshot: snapshot.getTiles()) {
       	   		String[] tileBits = tileSnapshot.getName().split(Constants.COLON);
       			if (tileBits.length > 1) {
       	    		String tileSetName = tileBits[0];
       	    		TileSet tileSet = getTileSet(tileSetName, tileSets);
       	    		if (tileSet == null) {
       	    			System.out.println("tile set not found: " + tileSetName);
       	    		}
       	    		else {
       	   	    		Tile tempTile = tileSet.getTile(tileBits[1]);
       	   	    		if (tempTile != null) {
       	   		    		Tile tile = tileConversion.convertTile(tempTile);
       	   		    		String maskLevel = tileSnapshot.getMaskLevel();
       	   		    		if (maskLevel == null) {
       	   		    			mapTile.addTile(tile);
       	   		    		}
       	   		    		else {
       	   		    			mapTile.addTile(tile, maskLevel);
       	   		    		}
       	   	    		}
       	    		}
       			}
       		}
    	}   	   		
    }
    
    private void initialiseMap(Point size) {
		// create an empty map image
    	this.size = size;
    	int rows = size.y, cols = size.x;
		mapImage = new Image(DisplayHelper.getDisplay(),
				cols * TILE_SIZE, rows * TILE_SIZE);
		
		// now draw the tiles
    	mapTiles = new MapTile[cols][rows];
		Image[] baseTiles = new Image[2];
		PaletteData paletteData = new PaletteData(new RGB[] { COLOUR_A });
		ImageData imageData = new ImageData(TILE_SIZE, TILE_SIZE, 1, paletteData);
		baseTiles[0] = new Image(DisplayHelper.getDisplay(), imageData);
		paletteData = new PaletteData(new RGB[] { COLOUR_B });
		imageData = new ImageData(TILE_SIZE, TILE_SIZE, 1, paletteData);
		baseTiles[1] = new Image(DisplayHelper.getDisplay(), imageData);
		for (int y = 0; y < rows; y++) {
			for (int x = 0; x < cols; x++) {
				// MapTile mapTile = mapTiles[x][y];
				mapTiles[x][y] = new MapTile(baseTiles[(x + y + 1) % 2]);
				updateTileImage(mapTiles[x][y], new Point(x, y));
			}
		}
    }

    public void saveRpgMap() {
    	saveRpgMap(false);
    }

    public void saveRpgMap(boolean saveAs) {    	
    	if ((path == null) || saveAs) {
        	FileDialog dialog = new FileDialog(DisplayHelper.getShell(), SWT.SAVE);
    		dialog.setFilterPath(mapsPath);
        	dialog.setText("Save map or cancel");
        	path = dialog.open();
        	if (path == null) {
        		return;
        	}
    	}
    	BufferedWriter writer = null;
    	try {
        	writer = new BufferedWriter(new FileWriter(path));
        	int rows = size.y, cols = size.x;
    		for (int y = 0; y < rows; y++) {
    			for (int x = 0; x < cols; x++) {
        			StringBuffer buffer = new StringBuffer();
        			buffer.append(x + Constants.COMMA + y);
        			buffer.append(mapTiles[x][y]);
        			writer.write(buffer.toString());
        			writer.newLine();
    			}
        		writer.newLine();
    		}
        	writer.flush();
    	}
    	catch (Exception e) {
    		e.printStackTrace();
    	}
    	finally {
    		if (writer != null) {
    			try {
        			writer.close();
        			writer = null;
    			}
    			catch (Exception e) { ; }
    		}
    	}
    }
    
    public Image getMapImage() {
    	return mapImage;
    }
    
    public MapTile getMapTile(Point tilePoint) {
    	return mapTiles[tilePoint.x][tilePoint.y];
    }
    
    // ** TILE UPDATE METHODS **
    
    public void addTile(Point tilePoint, Tile tile) {
		MapTile mapTile = getMapTile(tilePoint);
		mapTile.addTile(tile);
		updateTileImage(mapTile, tilePoint);    	
    }

    public void addTile(List<Point> tilePoints, Tile tile) {
		for (Point tilePoint: tilePoints) {
			addTile(tilePoint, tile);
		}
    }

    public void insertTile(Point tilePoint, Tile tile) {
		MapTile mapTile = getMapTile(tilePoint);
		mapTile.replaceTiles(tile);
		updateTileImage(mapTile, tilePoint);    	
    }
    
    public void insertTile(List<Point> tilePoints, Tile tile) {
		for (Point tilePoint: tilePoints) {
			insertTile(tilePoint, tile);
		}
    }

    public void sendToBack(Point tilePoint) {
		MapTile mapTile = getMapTile(tilePoint);
		mapTile.sendToBack();
		updateTileImage(mapTile, tilePoint);
    }
    
    public void sendToBack(List<Point> tilePoints) {
		for (Point tilePoint: tilePoints) {
			sendToBack(tilePoint);
		}
    }

    public void keepTop(Point tilePoint) {
		MapTile mapTile = getMapTile(tilePoint);
		mapTile.keepTopTile();
		updateTileImage(mapTile, tilePoint);    	
    }

    public void keepTop(List<Point> tilePoints) {
		for (Point tilePoint: tilePoints) {
			keepTop(tilePoint);
		}
    }

    public void clear(Point tilePoint) {
		MapTile mapTile = getMapTile(tilePoint);
		mapTile.clearTiles();
		updateTileImage(mapTile, tilePoint);    	
    }

    public void clear(List<Point> tilePoints) {
		for (Point tilePoint: tilePoints) {
			clear(tilePoint);
		}
    }
    
    public MapTileSnapshot getSnapshot(Point tilePoint) {
		MapTile mapTile = getMapTile(tilePoint);
		return mapTile.getSnapshot();
    }
    
    public MapSnapshot getSnapshot(List<Point> tilePoints) {
    	Map<Point, MapTileSnapshot> tileSnapshots = new HashMap<Point, MapTileSnapshot>();
    	for (Point tilePoint: tilePoints) {
    		tileSnapshots.put(tilePoint, getSnapshot(tilePoint));
    	}
    	return new MapSnapshot(tileSnapshots);
    }
    
    public void paste(Point tilePoint, MapSnapshot mapSnapshot) {
	    Map<String, TileSet> tileSets = new HashMap<String, TileSet>();
    	MapTileSnapshot[][] tileSnapshots = mapSnapshot.getMapTiles();
    	Point snapshotSize = mapSnapshot.getSize();
    	int sRows = snapshotSize.y, sCols = snapshotSize.x;
    	int rows = size.y, cols = size.x;
    	for (int x = 0; x < sCols; x++) {
    		for (int y = 0; y < sRows; y++) {
    			int tx = x + tilePoint.x;
    			int ty = y + tilePoint.y;
    			if ((tx < cols) && (ty < rows)) {
    				MapTile mapTile = mapTiles[tx][ty];
    				pasteIntoMapTile(mapTile, tileSnapshots[x][y], tileSets);
    		    	updateTileImage(mapTile, new Point(tx, ty));
    			}
    		}
    	}
    }
    
    public boolean resize(int left, int right, int top, int bottom) {
    	boolean resized = false;
    	System.out.println("left: " + left);
    	System.out.println("right: " + right);
    	System.out.println("top: " + top);
    	System.out.println("bottom: " + bottom);
    	int oldRows = size.y, oldCols = size.x;
    	int rows = Math.min(oldRows + top + bottom, 64);
    	int cols = Math.min(oldCols + left + right, 64);
    	if ((rows > 0) && (cols > 0)) {
    		MapTile[][] oldMapTiles = mapTiles;
    	    initialiseMap(new Point(cols, rows));
    	    System.out.println(size);
        	for (int x = 0; x < oldCols; x++) {
        		for (int y = 0; y < oldRows; y++) {
        			int tx = x + left;
        			int ty = y + top;
        			if ((tx < cols) && (ty < rows)) {
        				MapTile oldMapTile = oldMapTiles[x][y];
        				MapTile mapTile = mapTiles[tx][ty];
        				mapTile.setTiles(oldMapTile.getTiles());
        				mapTile.setLevels(oldMapTile.getLevels());
        		    	updateTileImage(mapTile, new Point(tx, ty));
        			}
        		}
        	}
        	resized = true;
    	}
    	return resized;
    }
    
	public void updateTileImage(MapTile mapTile, Point tilePoint) {
		GC gc = new GC(mapImage);
		int x = tilePoint.x * TILE_SIZE;
		int y = tilePoint.y * TILE_SIZE;
		gc.drawImage(mapTile.getBaseTile(), x, y);
		List<MaskTile> tiles = mapTile.getTiles();
		if (tiles != null) {
			for (MaskTile tile: tiles) {
				gc.drawImage(tile.getTile().getImage(), x, y);								
			}			
		}			
		// must dispose the context or we get an error second time around
		gc.dispose();						
	}
}

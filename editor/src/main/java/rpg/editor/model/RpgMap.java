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
    
    private void initialiseMap(Point size) {
    	// initialise the map tiles
    	this.size = size;
    	int rows = size.y, cols = size.x;
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
				mapTiles[x][y] = new MapTile(baseTiles[(x + y + 1) % 2]);
			}
		}

		// create an empty map image with chess board pattern
		paletteData = new PaletteData(new RGB[] { COLOUR_A, COLOUR_B });
		imageData = new ImageData(cols, rows, 1, paletteData);
		for (int x = 0; x < cols; x += 2) {
			for (int y = 0; y < rows; y++) {
				imageData.setPixel(x + (y % 2), y, 1);
			}
		}
		mapImage = new Image(DisplayHelper.getDisplay(),
	    		imageData.scaledTo(cols * TILE_SIZE, rows * TILE_SIZE));    	
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
    
    public void insertTile(Point tilePoint, Tile tile) {
		MapTile mapTile = getMapTile(tilePoint);
		mapTile.replaceTiles(tile);
		updateTileImage(mapTile, tilePoint);    	
    }
    
    public void sendToBack(Point tilePoint) {
		MapTile mapTile = getMapTile(tilePoint);
		mapTile.sendToBack();
		updateTileImage(mapTile, tilePoint);
    }
    
    public void keepTop(Point tilePoint) {
		MapTile mapTile = getMapTile(tilePoint);
		mapTile.keepTopTile();
		updateTileImage(mapTile, tilePoint);    	
    }
    
    public void clear(Point tilePoint) {
		MapTile mapTile = getMapTile(tilePoint);
		mapTile.clearTiles();
		updateTileImage(mapTile, tilePoint);    	
    }
    
	public void updateTileImage(MapTile mapTile, Point tilePoint) {
		int x = tilePoint.x * TILE_SIZE;
		int y = tilePoint.y * TILE_SIZE;
		GC gc = new GC(mapImage);
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

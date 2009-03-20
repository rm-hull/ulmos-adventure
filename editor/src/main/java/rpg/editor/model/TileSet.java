package rpg.editor.model;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.widgets.FileDialog;

import rpg.editor.Constants;
import rpg.editor.core.DisplayHelper;
import rpg.editor.core.ViewSize;

/**
 * Represents a set of tiles, including functionality to load a tile set from disk.
 * @author seldred
 */
public class TileSet {

	private static final String TILES_PROPERTIES = "tiles.properties";

	private static final String TILES_PATH = "tiles.path";
	private static final String TILES_EXTENSION = "tiles.extension";	
	private static final String METADATA_EXTENSION = "metadata.extension";
	
	private static String tilesPath;
	private static String tilesExtension;
	private static String metadataExtension;
	
	private static String[] validExtensions;
	
	private static final int TILE_SIZE = ViewSize.MEDIUM.getTileSize();
	
    private Map<ViewSize, Image> tilesImages = new HashMap<ViewSize, Image>();
    
	private Map<String, Point> namePointMappings = new HashMap<String, Point>();
	
    private Tile[][] tiles;
    
	private String name;
	
	static {
		try {
			InputStream input = ClassLoader.getSystemResourceAsStream(TILES_PROPERTIES);
			Properties properties = new Properties();
			properties.load(input);
			tilesPath = properties.getProperty(TILES_PATH);
			if (tilesPath.charAt(tilesPath.length() - 1) != Constants.SLASH) {
				tilesPath = tilesPath + Constants.SLASH;
			}
			tilesExtension = properties.getProperty(TILES_EXTENSION);
			if (tilesExtension.charAt(0) != Constants.DOT) {
				tilesExtension = Constants.DOT + tilesExtension;
			}
			metadataExtension = properties.getProperty(METADATA_EXTENSION);
			validExtensions = new String[] { Constants.STAR + tilesExtension };
			logProperties();
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	private static void logProperties() {
		System.out.println("tile set properties");
		System.out.println("- " + TILES_PATH + ": " + tilesPath);
		System.out.println("- " + TILES_EXTENSION + ": " + tilesExtension);
		System.out.println("- " + METADATA_EXTENSION + ": " + metadataExtension);
	}
	
	public static TileSet loadTileSet() {
		FileDialog dialog = new FileDialog(DisplayHelper.getShell(), SWT.OPEN);
		dialog.setFilterPath(tilesPath);
		dialog.setFilterExtensions(validExtensions);
		dialog.setText("Open an image file or cancel");
		String path = dialog.open();
		if (path != null) {
			String name = removeExtension(dialog.getFileName());
			return loadTileSet(path, name);
		}
		return null;
	}
	
	public static TileSet loadTileSet(String name) {
		return loadTileSet(tilesPath + name + tilesExtension, name);
	}
	
	private static TileSet loadTileSet(String path, String name) {
		System.out.println("requested tile set: " + path);
		TileSet tileSet = null;
		File imageFile = new File(path);
		if (imageFile.exists()) {
			try {
				Image tiles = new Image(DisplayHelper.getDisplay(), path);
				File metadata = new File(removeExtension(path) + metadataExtension);
				if (metadata.exists()) {
					tileSet = new TileSet(name, tiles, metadata);
				}
				else {
					System.out.println("metadata not found: " + metadata);
				}
			}
			catch (Exception e) {
				e.printStackTrace();
			}			
		}
		return tileSet;
	}
	
	private static String removeExtension(String filename) {
		int extIndex = filename.lastIndexOf('.');
		return filename.substring(0, extIndex);
	}
	
	private TileSet(String name, Image tilesImage, File metadata) {
		this.name = name;

		// create tile images
	    tilesImages.put(ViewSize.SMALL, tilesImage);
	    int width = tilesImage.getBounds().width;
	    int height = tilesImage.getBounds().height;
	    tilesImages.put(ViewSize.MEDIUM, new Image(DisplayHelper.getDisplay(), tilesImage.getImageData()
	    		.scaledTo(width * ViewSize.MEDIUM.getScalar(), height * ViewSize.MEDIUM.getScalar())));
	    tilesImages.put(ViewSize.LARGE, new Image(DisplayHelper.getDisplay(), tilesImage.getImageData()
	    		.scaledTo(width * ViewSize.LARGE.getScalar(), height * ViewSize.LARGE.getScalar())));
	    
	    // load metadata
	    Map<Point, String> tileNames = new HashMap<Point, String>();
	    int maxX = 0, maxY = 0;
	    BufferedReader reader = null;
	    try {
		    reader = new BufferedReader(new FileReader(metadata));
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
				    	if (bits.length == 2) {
					    	String tileName = bits[1].trim();
					    	if (tileName.length() > 0) {
						    	Point tilePoint = new Point(x, y);
						    	tileNames.put(tilePoint, tileName);
						    	if (namePointMappings.containsKey(tileName)) {
						    		System.out.println("WARNING: duplicate tile name!");
						    	}
						    	else {
							    	namePointMappings.put(tileName, tilePoint);					    		
						    	}
					    	}
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
	    
	    // create tiles
	    tiles = new Tile[++maxX][++maxY];
	    for (Point tilePoint: tileNames.keySet()) {
	    	int x = tilePoint.x, y = tilePoint.y;
    		tiles[x][y] = new Tile(name + Constants.COLON + tileNames.get(tilePoint),
    				getTileImage(x, y));
	    }
	}
	
	public String getName() {
		return name;
	}
	
	public Image getTilesImage(ViewSize viewSize) {
		return tilesImages.get(viewSize);
	}

	public Tile getTile(Point tilePoint) {
		int x = tilePoint.x, y = tilePoint.y;
		if ((x < tiles.length) && (y < tiles[x].length)) {
			return tiles[x][y];			
		}
		return null;
	}
	
	public Tile getTile(String tileName) {
		if (namePointMappings.containsKey(tileName)) {
			Point tilePoint = namePointMappings.get(tileName);
			return getTile(tilePoint);
		}
		System.out.println("tile not found: " + name + ":" + tileName);
		return null;
	}
	
	private Image getTileImage(int x, int y) {
		// int tileSize = ViewSize.MEDIUM.getTileSize();
		Image tileImage = new Image(DisplayHelper.getDisplay(), TILE_SIZE, TILE_SIZE);
		GC gc = new GC(tileImage);
		gc.drawImage(tilesImages.get(ViewSize.MEDIUM), x * TILE_SIZE, y * TILE_SIZE,
				TILE_SIZE, TILE_SIZE, 0, 0, TILE_SIZE, TILE_SIZE);
		gc.dispose();
		return tileImage;
	}
	
	public void dispose() {
		for (Image image: tilesImages.values()) {
			image.dispose();
		}
	}
	
	public static void main(String[] args) {
		TileSet tileSet = TileSet.loadTileSet("earth");
		System.out.println(tileSet.getName());
		System.out.println(tileSet.getTile(new Point(4, 1)).getName());
		System.out.println(tileSet.getTile(new Point(1, 2)).getName());
		System.out.println(tileSet.getTile(new Point(8, 4)));
		System.out.println(tileSet.getTile("mlrs").getName());
	}
}

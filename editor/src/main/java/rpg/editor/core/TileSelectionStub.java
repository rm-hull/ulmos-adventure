package rpg.editor.core;

import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.ImageData;

import rpg.editor.model.Tile;
import rpg.editor.model.TileSet;

/**
 * Functional TileSelection stub so that we can run the TilePicker and MapEditor
 * components in isolation. 
 * @author seldred
 */
public class TileSelectionStub implements TileSelection, TileConversion {

	private Tile tile;

	// == SINGLETON ==
	
	private static TileSelectionStub instance = new TileSelectionStub();
	
	private TileSelectionStub() {
		TileSet tileSet = TileSet.loadTileSet("grass");
		tile = convertTile(tileSet.getTile("tr2"));
	}
	
	public static TileSelectionStub getInstance() {
		return instance;
	}

	// ===============

	public void tileSelected(Tile tile) {
		System.out.println("tile selected: " + tile.getName());
	}
	
	public Tile convertTile(Tile tile) {
		ImageData imageData = tile.getImage().getImageData();
		// PaletteData paletteData = imageData.palette;
		// imageData.transparentPixel = paletteData.getPixel(ImageHelper.TRANSPARENT_COLOUR);
		imageData.transparentPixel = 65344;  // hack required for macosx cocoa
        /*byte[] alphaValues = new byte[imageData.height * imageData.width];
        for(int x = 0; x < imageData.width; x++) {
        	for(int y = 0; y < imageData.height; y++) {
        		int index = y * imageData.width + x;
        		System.out.println(String.format("(%s, %s) : %s", x, y, imageData.getPixel(x, y)));
        		if (index % 2 == 0) {
        			alphaValues[index] = 0;
        		}
        		else {
        			alphaValues[index] = (byte) 255;
        		}
        	}
        }
        imageData.alphaData = alphaValues;*/
		Image transparentImage = new Image(DisplayHelper.getDisplay(), imageData);
		// System.out.println(transparentImage.getImageData().transparentPixel);
		// System.out.println(transparentImage.getImageData().alphaData);
		return new Tile(tile.getName(), transparentImage);		
	}
		
	public Tile getSelectedTile() {
		return tile;
	}

	public boolean isTileSelected() {
		return true;
	}
}

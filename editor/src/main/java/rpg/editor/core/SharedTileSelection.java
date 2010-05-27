package rpg.editor.core;

import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.graphics.PaletteData;

import rpg.editor.model.Tile;

public class SharedTileSelection implements TileSelection, TileConversion {

	private Tile tile;

	// == SINGLETON ==
	
	private static SharedTileSelection instance = new SharedTileSelection();
	
	private SharedTileSelection() {
	}

	public static SharedTileSelection getInstance() {
		return instance;
	}

	// ===============

	public void tileSelected(Tile tile) {
		this.tile = convertTile(tile);
	}
	
	public Tile convertTile(Tile tile) {
		ImageData imageData = tile.getImage().getImageData();
		PaletteData paletteData = imageData.palette;
		imageData.transparentPixel = paletteData.getPixel(ImageHelper.TRANSPARENT_COLOUR);
		// imageData.transparentPixel = 65344; // hack required for macosx cocoa
		Image transparentImage = new Image(DisplayHelper.getDisplay(), imageData);
		return new Tile(tile.getName(), transparentImage);		
	}
	
	public Tile getSelectedTile() {
		return tile;
	}

	public boolean isTileSelected() {
		if (tile == null) {
			return false;
		}
		return true;
	}
}

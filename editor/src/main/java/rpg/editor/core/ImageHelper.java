package rpg.editor.core;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.graphics.PaletteData;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.widgets.Display;

public class ImageHelper {
	
	private static final int TILE_SIZE = ViewSize.SMALL.getTileSize();
	
	public static final RGB HIGHLIGHT_COLOUR = new RGB(255, 255, 255);
	public static final RGB SELECTED_COLOUR = new RGB(255, 0, 0);
	public static final RGB TRANSPARENT_COLOUR = new RGB(0, 255, 0);

	private static Map<ViewSize, Image> highlightImages = new HashMap<ViewSize, Image>();
	private static Map<ViewSize, Image> selectedImages = new HashMap<ViewSize, Image>();
	
	static {
		Display display = DisplayHelper.getDisplay();
		
		// highlight images
		ImageData imageData = getImageData(HIGHLIGHT_COLOUR);
		Image baseImage = new Image(display, imageData);
	    highlightImages.put(ViewSize.SMALL, new Image(display, baseImage.getImageData()));
	    highlightImages.put(ViewSize.MEDIUM, new Image(display,
	    		baseImage.getImageData().scaledTo(ViewSize.MEDIUM.getTileSize(), ViewSize.MEDIUM.getTileSize())));
	    highlightImages.put(ViewSize.LARGE, new Image(display,
	    		baseImage.getImageData().scaledTo(ViewSize.LARGE.getTileSize(), ViewSize.LARGE.getTileSize())));

	    // selected images
		imageData = getImageData(SELECTED_COLOUR);
		baseImage = new Image(display, imageData);
		selectedImages.put(ViewSize.SMALL, new Image(display, baseImage.getImageData()));
		selectedImages.put(ViewSize.MEDIUM, new Image(display,
	    		baseImage.getImageData().scaledTo(ViewSize.MEDIUM.getTileSize(), ViewSize.MEDIUM.getTileSize())));
		selectedImages.put(ViewSize.LARGE, new Image(display,
	    		baseImage.getImageData().scaledTo(ViewSize.LARGE.getTileSize(), ViewSize.LARGE.getTileSize())));
	}
	
	private static ImageData getImageData(RGB colour) {
		// create the palette data we require
		PaletteData paletteData = new PaletteData(new RGB[] { colour, TRANSPARENT_COLOUR });
		// and construct image data
		ImageData imageData = new ImageData(TILE_SIZE, TILE_SIZE, 1, paletteData);
		for (int x = 1; x < TILE_SIZE - 1; x++) {
			for (int y = 1; y < TILE_SIZE - 1; y++) {
				imageData.setPixel(x, y, 1);
			}
		}
		imageData.transparentPixel = paletteData.getPixel(TRANSPARENT_COLOUR);
		return imageData;
	}
	
	public static Image getHighlightImage(ViewSize viewSize) {
		return highlightImages.get(viewSize);
	}

	public static Image getSelectedImage(ViewSize viewSize) {
		return selectedImages.get(viewSize);
	}
	
	public static void dispose() {
		for (Image image: highlightImages.values()) {
			image.dispose();
		}
		for (Image image: selectedImages.values()) {
			image.dispose();
		}
	}
}

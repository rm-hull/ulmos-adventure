package rpg.editor.model;

import org.eclipse.swt.graphics.Image;

/**
 * Represents a tile in a TileSet and forms part of MapTile when added to an RpgMap.
 * @author seldred
 */
public class Tile {

	private String name;
	
	private Image image;
	
	public Tile(String name, Image image) {
		this.name = name;
		this.image = image;
	}

	public String getName() {
		return name;
	}

	public Image getImage() {
		return image;
	}

	public String toString() {
		return name;
	}
	
	public void dispose() {
		image.dispose();
	}
}

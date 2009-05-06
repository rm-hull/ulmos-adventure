package rpg.editor.core;

import rpg.editor.model.Tile;

/**
 * Defines an interface for converting non-transparent tiles (as they appears in
 * the TilePicker) to transparent.
 * 
 * @author seldred
 */
public interface TileConversion {

	public Tile convertTile(Tile tile);
}

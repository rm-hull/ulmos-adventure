package rpg.editor.core;

import rpg.editor.model.Tile;

/**
 * Defines an interface for selecting a tile and then retrieving it.  An
 * implementation of this class is referenced by the three main components:
 * TilePicker, RecentTiles and MapEditor.
 * 
 * RecentTiles also implements this interface itself and acts as a proxy
 * between the TilePicker and the SharedTileSelection.
 *  
 * @author seldred
 */
public interface TileSelection {
	
	public void tileSelected(Tile tile);
	
	public Tile getSelectedTile();
	
	public boolean isTileSelected();
}

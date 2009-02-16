package rpg.editor.model;

import java.util.ArrayList;
import java.util.List;
import java.util.ListIterator;

import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.widgets.Composite;

import rpg.editor.Constants;
import rpg.editor.components.DisplayHelper;
import rpg.editor.components.TileEditDialog;
import rpg.editor.components.TileEditor;
import rpg.editor.components.TileEditorFactory;
import rpg.editor.components.TileImagesEditor;
import rpg.editor.components.TileLevelsEditor;
import rpg.editor.components.TileMasksEditor;

/**
 * Represents a tile in an RpgMap.  The relationship between the tiles is:
 * MapTile -> *MaskTile -> Tile
 * 
 * Since a MapTile can contain multiple tiles, this allows the user to build
 * a map tile by layering tiles on top of each other. This is also where level
 * data is stored.
 * 
 * @author seldred
 */
public class MapTile {
	
	private Image baseTile;
	
	private List<MaskTile> tiles;
	
	private String[] levels;
	
	public MapTile(Image myBaseTile) {
		baseTile = myBaseTile;
	}

	public List<MaskTile> getTiles() {
		return tiles;
	}

	public int getTileDepth() {
		if (tiles == null) {
			return 0;
		}
		return tiles.size();
	}
	
	public String[] getLevels() {
		return levels;
	}
	
	public void setLevels(String[] levels) {
		this.levels = levels;
	}

	public Image getBaseTile() {
		return baseTile;
	}

	public void addTile(Tile tile) {
		if (tiles == null) {
			tiles = new ArrayList<MaskTile>();
		}
		tiles.add(new MaskTile(tile));
	}
	
	public void addTile(Tile tile, String maskLevel) {
		if (tiles == null) {
			tiles = new ArrayList<MaskTile>();
		}
		tiles.add(new MaskTile(tile, maskLevel));
	}
	
	public void replaceTiles(Tile tile) {
		tiles = new ArrayList<MaskTile>();
		tiles.add(new MaskTile(tile));
	}
	
	public void setTiles(List<MaskTile> tiles) {
		this.tiles = tiles;
	}

	public void keepTopTile() {
		List<MaskTile> newTiles = new ArrayList<MaskTile>();
		newTiles.add(tiles.get(tiles.size() - 1));
		tiles = newTiles;
	}
	
	public void clearTiles() {
		tiles = null;
	}
	
	public void sendToBack() {
		List<MaskTile> newTiles = new ArrayList<MaskTile>();
		newTiles.add(tiles.get(tiles.size() - 1));
		for (MaskTile tile: tiles) {
			if (newTiles.size() < tiles.size()) {
				newTiles.add(tile);
			}
		}
		tiles = newTiles;
	}

	public void editImages() {
		if (tiles != null) {
			TileEditorFactory editorFactory = new TileImagesEditorFactory();
			TileEditDialog tileEditor = new TileEditDialog(DisplayHelper.getShell(), editorFactory);
			tileEditor.editTile(this);			
		}
	}
	
	public void editMasks() {
		if (tiles != null) {
			TileEditorFactory editorFactory = new TileMasksEditorFactory();
			TileEditDialog tileEditor = new TileEditDialog(DisplayHelper.getShell(), editorFactory);
			tileEditor.editTile(this);			
		}
	}
	
	public void editLevels() {
		TileEditorFactory editorFactory = new TileLevelsEditorFactory();
		// need to set width and height on this one or it displays too small
		TileEditDialog tileEditor = new TileEditDialog(DisplayHelper.getShell(), 240, 320, editorFactory);
		tileEditor.editTile(this);			
	}
	
	public void dispose() {
		baseTile.dispose();
		if (tiles != null) {
			for (MaskTile tile: tiles) {
				tile.getTile().getImage().dispose();
			}			
		}
	}
	
	public String toString() {
		if (tiles == null) {
			return Constants.EMPTY;
		}
		StringBuffer buffer = new StringBuffer();
		if (levels != null) {
			buffer.append(Constants.SPACE + levelsToString(Constants.COMMA));
		}
		for (MaskTile tile: tiles) {
			buffer.append(Constants.SPACE + tile.getTile().getName());
			String maskLevel = tile.getMaskLevel();
			if (maskLevel != null) {
				buffer.append(Constants.COLON + maskLevel);
			}
		}			
		return buffer.toString();
	}
	
	// for external use
	public String getLabel() {
		StringBuffer buffer = new StringBuffer();
		buffer.append(getTileDepth());
		buffer.append(Constants.SPACE + getLevelsLabel());
		buffer.append(Constants.SPACE + getMasksLabel());
		return buffer.toString(); 
	}
	
	private String getLevelsLabel() {
		if (levels == null) {
			return Constants.EMPTY_ARRAY;
		}
		return levelsToString(Constants.LABEL_COMMA);
	}
	
	private String getMasksLabel() {
		if (tiles == null) {
			return Constants.EMPTY_ARRAY;
		}
		StringBuffer buffer = new StringBuffer();
		buffer.append(Constants.OPEN_SQ_BRACKET);
		boolean firstItem = true;
		ListIterator<MaskTile> iterator = tiles.listIterator(tiles.size());
		while (iterator.hasPrevious()) {
			MaskTile tile = iterator.previous();
			if (tile.getMaskLevel() != null) {
				if (firstItem) {
					firstItem = false;
				}
				else {
					buffer.append(Constants.LABEL_COMMA);
				}
				buffer.append(tile.getMaskLevel());
			}
		}
		buffer.append(Constants.CLOSE_SQ_BRACKET);
		return buffer.toString();
	}
	
	private String levelsToString(String comma) {
		StringBuffer buffer = new StringBuffer();
		buffer.append(Constants.OPEN_SQ_BRACKET);
		for (int i = 0; i < levels.length; i++) {
			buffer.append(levels[i]);
			if (i + 1 < levels.length) buffer.append(comma); 
		}
		buffer.append(Constants.CLOSE_SQ_BRACKET);
		return buffer.toString();
	}
	
	// =======================================
	// == inner class tile editor factories ==
	// =======================================
	
	public static class TileImagesEditorFactory implements TileEditorFactory {
		public TileEditor newTileEditor(Composite myParent, MapTile mapTile) {
			return new TileImagesEditor(myParent, mapTile);
		}
	}
	
	public static class TileLevelsEditorFactory implements TileEditorFactory {
		public TileEditor newTileEditor(Composite myParent, MapTile mapTile) {
			return new TileLevelsEditor(myParent, mapTile);
		}
	}
	
	public static class TileMasksEditorFactory implements TileEditorFactory {
		public TileEditor newTileEditor(Composite myParent, MapTile mapTile) {
			return new TileMasksEditor(myParent, mapTile);
		}
	}
}

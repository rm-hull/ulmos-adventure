package rpg.editor.components;

import org.eclipse.swt.widgets.Composite;

import rpg.editor.model.MapTile;

public abstract class TileEditor extends Composite {

	private MapTile mapTile;
	
	public TileEditor(Composite parent, int style, MapTile mapTile) {
		super(parent, style);
		this.mapTile = mapTile;
	}
	
	public abstract void applyChanges();

	public MapTile getMapTile() {
		return mapTile;
	}
}

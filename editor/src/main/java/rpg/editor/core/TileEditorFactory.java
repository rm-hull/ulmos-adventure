package rpg.editor.core;

import org.eclipse.swt.widgets.Composite;

import rpg.editor.model.MapTile;

public interface TileEditorFactory {
	
	public TileEditor newTileEditor(Composite parent, MapTile mapTile);
}

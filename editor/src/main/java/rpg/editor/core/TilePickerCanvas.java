package rpg.editor.core;

import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.widgets.Composite;

/**
 * Includes common functionality for the tile pickers: TilePicker and RecentTiles.
 * @author seldred
 */
public abstract class TilePickerCanvas extends TileCanvas {

	public TilePickerCanvas(Composite parent) {
		super(parent);

		addMouseListener(new MouseAdapter() {
			@Override
			public void mouseDown(MouseEvent e) {
				if (!highlightTile.equals(NO_SELECTION)) {
					Point previousSelectedTile = selectedTile;
					Point tempSelectedTile = highlightTile;
					if (!tempSelectedTile.equals(previousSelectedTile) &&
							isSelectionValid(tempSelectedTile)) {
						selectedTile = tempSelectedTile;
						redraw();
						tileSelectedAction();
					}					
				}
			}
		});
	}
	
	public abstract boolean isSelectionValid(Point tilePoint);
	
	public abstract void tileSelectedAction();
}

package rpg.editor.components;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;

import rpg.editor.Constants;
import rpg.editor.core.DisplayHelper;
import rpg.editor.core.ImageHelper;
import rpg.editor.core.TilePickerCanvas;
import rpg.editor.core.TileSelection;
import rpg.editor.core.TileSelectionStub;
import rpg.editor.core.ViewSize;
import rpg.editor.model.Tile;
import rpg.editor.model.TileSet;

/**
 * Component that allows the user to pick a tile from a TileSet.
 * 
 * @author seldred
 */
public class TilePicker extends Composite {

	private ScrolledComposite canvasHolder;

	private TileSetCanvas tileSetCanvas;

	public TilePicker(Composite parent, TileSet tileSet) {
		this(parent, SWT.NONE, tileSet);
	}

	public TilePicker(Composite parent, int style, TileSet tileSet) {

		super(parent, style);
		// this.tileSet = tileSet;

		// layout setup
		setLayout(new GridLayout());
		setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

		// radio buttons
		Group radioGroup = new Group(this, SWT.SHADOW_ETCHED_IN);
		radioGroup.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true,
				false));
		radioGroup.setLayout(new RowLayout());
		Button smallButton = new Button(radioGroup, SWT.RADIO);
		smallButton.setText(ViewSize.SMALL.getLabel());
		smallButton.setSelection(false);
		Button mediumButton = new Button(radioGroup, SWT.RADIO);
		mediumButton.setText(ViewSize.MEDIUM.getLabel());
		mediumButton.setSelection(true);
		Button largeButton = new Button(radioGroup, SWT.RADIO);
		largeButton.setText(ViewSize.LARGE.getLabel());
		largeButton.setSelection(false);

		// canvas
		canvasHolder = new ScrolledComposite(this, SWT.H_SCROLL | SWT.V_SCROLL | SWT.BORDER);
		canvasHolder.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		tileSetCanvas = new TileSetCanvas(canvasHolder);
		tileSetCanvas.tileSet = tileSet;
		tileSetCanvas.tileImage = tileSet.getTilesImage(ViewSize.MEDIUM);
		canvasHolder.setContent(tileSetCanvas);
		canvasHolder.setExpandHorizontal(true);
		canvasHolder.setExpandVertical(true);
		Rectangle rect = tileSetCanvas.tileImage.getBounds();
		canvasHolder.setMinSize(rect.width, rect.height);

		// label
		Label tileLabel = new Label(this, SWT.CENTER);
		tileLabel.setText(Constants.NO_SELECTION_LABEL);
		tileLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		tileSetCanvas.tileLabel = tileLabel;

		// ** radio button listeners **
		smallButton.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				setViewSize(ViewSize.SMALL);
			}
		});
		mediumButton.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				setViewSize(ViewSize.MEDIUM);
			}
		});
		largeButton.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				setViewSize(ViewSize.LARGE);
			}
		});
	}

	public void setTileSelection(TileSelection tileSelection) {
		tileSetCanvas.tileSelection = tileSelection;
	}

	public void setViewSize(ViewSize viewSize) {
		tileSetCanvas.setViewSize(viewSize);
		Rectangle rect = tileSetCanvas.tileImage.getBounds();
		canvasHolder.setMinSize(rect.width, rect.height);
		tileSetCanvas.redraw();
	}

	// =====================================================
	// == main method to test this component in isolation ==
	// =====================================================
	
	public static void main(String[] args) throws Exception {

		Display display = DisplayHelper.getDisplay();
		Shell shell = DisplayHelper.getShell();
		shell.setLayout(new GridLayout());

		TileSet tileSet = TileSet.loadTileSet();
		TilePicker tilePicker = new TilePicker(shell, tileSet);
		tilePicker.setTileSelection(TileSelectionStub.getInstance());

		shell.setSize(800, 400);
		shell.open();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch())
				display.sleep();
		}

		// dispose resources
		tilePicker.dispose();
		ImageHelper.dispose();
		display.dispose();
	}
}

class TileSetCanvas extends TilePickerCanvas {

	protected TileSelection tileSelection;
	protected TileSet tileSet;
	protected Label tileLabel;

	public TileSetCanvas(Composite parent) {
		super(parent);
	}

	@Override
	public boolean isSelectionValid(Point tilePoint) {
		if (tileSet.getTile(tilePoint) == null) {
			return false;
		}
		return true;
	}

	@Override
	public void tileSelectedAction() {
		tileSelection.tileSelected(tileSet.getTile(selectedTile));
	}

	@Override
	public void setLabelText() {
		String labelText = Constants.NO_SELECTION_LABEL;
		if (highlightTile != null) {
			Tile tile = tileSet.getTile(highlightTile);
			if (tile != null) {
				labelText = highlightTile.x + Constants.LABEL_COMMA
						+ highlightTile.y + Constants.SEPARATOR
						+ tile.getName();
			}
		}
		tileLabel.setText(labelText);
	}
	
	public void setViewSize(ViewSize viewSize) {
		this.viewSize = viewSize;
		tileImage = tileSet.getTilesImage(viewSize);
	}
}

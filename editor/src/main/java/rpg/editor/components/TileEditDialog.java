package rpg.editor.components;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Dialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;

import rpg.editor.Constants;
import rpg.editor.core.DisplayHelper;
import rpg.editor.core.TileConversion;
import rpg.editor.core.TileEditor;
import rpg.editor.core.TileEditorFactory;
import rpg.editor.core.TileSelectionStub;
import rpg.editor.model.MapTile;
import rpg.editor.model.TileSet;

public class TileEditDialog extends Dialog {
	
	private TileEditorFactory editorFactory;
	
	private Point size = null;
	
	public TileEditDialog(Shell parent, TileEditorFactory editorFactory) {
		this(parent, editorFactory, SWT.NONE);
	}
	
	public TileEditDialog(Shell parent, TileEditorFactory editorFactory, int style) {
		super(parent, style);
		this.editorFactory = editorFactory;
	}
	
	public TileEditDialog(Shell parent, TileEditorFactory editorFactory, int width, int height) {
		this(parent, editorFactory, width, height, SWT.NONE);
	}
	
	public TileEditDialog(Shell parent, TileEditorFactory editorFactory, int width, int height, int style) {
		this(parent, editorFactory, style);
		size = new Point(width, height);
	}
	
	public void editTile(MapTile mapTile) {
		// setup
		Shell parent = getParent();
		final Shell shell = new Shell(parent, SWT.DIALOG_TRIM | SWT.APPLICATION_MODAL);
		shell.setText("Tile Editor");
		shell.setLayout(new GridLayout());
		
		// dialog specifics
		final TileEditor tileEditor = editorFactory.newTileEditor(shell, mapTile);
		Composite buttonBar = new Composite(shell, SWT.NONE);
		buttonBar.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false));
		buttonBar.setLayout(new RowLayout());
		Button ok = new Button(buttonBar, SWT.PUSH);
		ok.setText(Constants.OK);
		ok.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				tileEditor.applyChanges();
				shell.dispose();
			}
		});
		Button cancel = new Button(buttonBar, SWT.PUSH);
		cancel.setText(Constants.CANCEL);
		cancel.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				shell.dispose();
			}
		});
		if (size == null) {
			shell.pack();
		}
		else {
			shell.setSize(size);			
		}
		
		// center the dialog
		Rectangle parentBounds = parent.getBounds();
		Rectangle childBounds = shell.getBounds();
		int x = parentBounds.x + (parentBounds.width - childBounds.width) / 2;
		int y = parentBounds.y + (parentBounds.height - childBounds.height) / 2;
		shell.setLocation(x, y);
		
		// and display
		shell.open();
		Display display = parent.getDisplay();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) display.sleep();
		}
	}
	
	// =====================================================
	// == main method to test this component in isolation ==
	// =====================================================
	
	public static void main(String[] args) {
		
		Display display = DisplayHelper.getDisplay();
		Shell shell = DisplayHelper.getShell();
		
		TileConversion tileConversion = TileSelectionStub.getInstance();
		MapTile mapTile = new MapTile(null);
		TileSet tileSet = TileSet.loadTileSet("grass");
		mapTile.addTile(tileConversion.convertTile(tileSet.getTile("n1")));
		mapTile.addTile(tileConversion.convertTile(tileSet.getTile("n2")));
		tileSet = TileSet.loadTileSet("wood");
		mapTile.addTile(tileConversion.convertTile(tileSet.getTile("c_supp")), "2");
		mapTile.addTile(tileConversion.convertTile(tileSet.getTile("l_supp")));
		mapTile.setLevels(new String[] { "1", "S3", "2" });
		
		TileEditDialog tileEditor = new TileEditDialog(shell, new MapEditor.TileImagesEditorFactory());
		// TileEditDialog tileEditor = new TileEditDialog(shell, new MapEditor.TileLevelsEditorFactory());
		// TileEditDialog tileEditor = new TileEditDialog(shell, new MapEditor.TileMasksEditorFactory());
		tileEditor.editTile(mapTile);
		System.out.println(mapTile);
		
		display.dispose();
	}
}
 
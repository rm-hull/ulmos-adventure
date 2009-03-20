import rpg.editor.*
import rpg.editor.core.*
import rpg.editor.model.*
import org.eclipse.swt.*
import org.eclipse.swt.custom.*
import org.eclipse.swt.events.*
import org.eclipse.swt.graphics.*
import org.eclipse.swt.layout.*
import org.eclipse.swt.widgets.*

/**
 * Dialog for all tile edit operations.
 * 
 * @author seldred
 */
public class GTileEditDialog extends Dialog {
	
	def editorFactory;
	
	def size = null;
	
	public GTileEditDialog(parent, editorFactory, style = SWT.NONE) {
		super(parent, style);
		this.editorFactory = editorFactory;
	}
	
	public GTileEditDialog(parent, editorFactory, width, height, style = SWT.NONE) {
		this(parent, editorFactory, style)
		size = new Point(width, height);
	}
	
	public void editTile(mapTile) {
		// setup
		def parent = getParent();
		def shell = new Shell(parent, SWT.DIALOG_TRIM | SWT.APPLICATION_MODAL);
		shell.text = 'Tile Editor'
		shell.layout = new GridLayout();
		
		// dialog specifics
		def tileEditor = editorFactory.newTileEditor(shell, mapTile);
		def buttonBar = new Composite(shell, SWT.NONE);
		buttonBar.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false));
		buttonBar.setLayout(new RowLayout());
		def ok = new Button(buttonBar, SWT.PUSH);
		ok.setText(Constants.OK);
		ok.addListener(SWT.Selection, {
			tileEditor.applyChanges();
			shell.dispose();
		} as Listener);
		def cancel = new Button(buttonBar, SWT.PUSH);
		cancel.setText(Constants.CANCEL);
		cancel.addListener(SWT.Selection, {
			shell.dispose();
		} as Listener);
		if (size == null) {
			shell.pack();
		}
		else {
			shell.setSize(size);			
		}
		
		// center the dialog
		def parentBounds = parent.getBounds();
		def childBounds = shell.getBounds();
		int x = parentBounds.x + (parentBounds.width - childBounds.width) / 2;
		int y = parentBounds.y + (parentBounds.height - childBounds.height) / 2;
		shell.setLocation(x, y);
		
		// and display
		shell.open();
		def display = parent.getDisplay();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) display.sleep();
		}
	}
}

try {

def tileEditorFactory = {parent, mapTile ->
	return new TileImagesEditor(parent, mapTile);
	// return new TileLevelsEditor(parent, mapTile);
	// return new TileMasksEditor(parent, mapTile);
} as TileEditorFactory

def display = DisplayHelper.getDisplay();
def shell = DisplayHelper.getShell();

def tileConversion = TileSelectionStub.getInstance();
def mapTile = new MapTile(null);
def tileSet = TileSet.loadTileSet("grass");
mapTile.addTile(tileConversion.convertTile(tileSet.getTile("n1")));
mapTile.addTile(tileConversion.convertTile(tileSet.getTile("n2")));
tileSet = TileSet.loadTileSet("wood");
mapTile.addTile(tileConversion.convertTile(tileSet.getTile("c_supp")), "2");
mapTile.addTile(tileConversion.convertTile(tileSet.getTile("l_supp")));

String[] levels = ["1", "S3", "2"]
mapTile.setLevels(levels);

def tileEditor = new GTileEditDialog(shell, tileEditorFactory);
tileEditor.editTile(mapTile);
System.out.println(mapTile);

display.dispose();

}
catch (Exception e) {
	e.printStackTrace()
}
package rpg.editor.core;

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
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Spinner;

import rpg.editor.Constants;

public class NewMapDialog extends Dialog {
	
	private static final int DEFAULT_WIDTH = 16;
	private static final int DEFAULT_HEIGHT = 16;
	
	private Point mapSize;
	
	public NewMapDialog(Shell parent, int style) {
		super(parent, style);
	}
	
	public NewMapDialog(Shell parent) {
		this(parent, SWT.NONE);
	}
	
	public Point getSize() {
		return getSize(DEFAULT_WIDTH, DEFAULT_HEIGHT);
	}
	
	public Point getSize(int defaultWidth, int defaultHeight) {
		Shell parent = getParent();
		final Shell shell = new Shell(parent, SWT.DIALOG_TRIM | SWT.APPLICATION_MODAL);
		shell.setText("New Map");
		GridLayout gridLayout = new GridLayout();
		gridLayout.verticalSpacing = 12;
		gridLayout.marginWidth = 20;
		gridLayout.marginTop = 12;
		shell.setLayout(gridLayout);
		
		// width and height widgets
		Label label = new Label(shell, SWT.CENTER);
		label.setText("Enter new map size:");			
		label.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));
		Composite spinnerBox = new Composite(shell, SWT.NONE);
		spinnerBox.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false));
		spinnerBox.setLayout(new GridLayout(2, false));
		label = new Label(spinnerBox, SWT.CENTER);
		label.setText("Width:");			
		final Spinner widthInput = new Spinner(spinnerBox, SWT.NONE);
		widthInput.setMaximum(64);
		widthInput.setMinimum(8);
		widthInput.setSelection(defaultWidth);
		label = new Label(spinnerBox, SWT.CENTER);
		label.setText("Height:");			
		final Spinner heightInput = new Spinner(spinnerBox, SWT.NONE);
		heightInput.setMaximum(64);
		heightInput.setMinimum(8);
		heightInput.setSelection(defaultHeight);
		
		// ok + cancel buttons
		Composite buttonBar = new Composite(shell, SWT.NONE);
		buttonBar.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false));
		buttonBar.setLayout(new RowLayout());
		Button ok = new Button(buttonBar, SWT.PUSH);
		ok.setText(Constants.OK);
		ok.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				mapSize = new Point(widthInput.getSelection(), heightInput.getSelection());
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
		
		// center the dialog
		shell.pack();		
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
		
		return mapSize;
	}
}

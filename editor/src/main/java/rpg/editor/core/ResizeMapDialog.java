package rpg.editor.core;

import org.eclipse.swt.SWT;
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

public class ResizeMapDialog extends Dialog {
	
	private static final int ZERO = 0;
	
	private int[] adjustments;
	
	public ResizeMapDialog(Shell parent, int style) {
		super(parent, style);
	}
	
	public ResizeMapDialog(Shell parent) {
		this(parent, SWT.NONE);
	}

	public int[] getAdjustments() {
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
		label.setText("Resize map:");			
		label.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));

		final Spinner topInput = getSpinner(shell, "Top");
		Composite spinnerRow = new Composite(shell, SWT.NONE);
		spinnerRow.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false));
		spinnerRow.setLayout(new GridLayout(2, false));
		final Spinner leftInput = getSpinner(spinnerRow, "Left");
		final Spinner rightInput = getSpinner(spinnerRow, "Right");
		final Spinner bottomInput = getSpinner(shell, "Bottom");
				
		// ok + cancel buttons
		Composite buttonBar = new Composite(shell, SWT.NONE);
		buttonBar.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false));
		buttonBar.setLayout(new RowLayout());
		Button ok = new Button(buttonBar, SWT.PUSH);
		ok.setText(Constants.OK);
		ok.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				adjustments = new int[4];
				adjustments[0] = leftInput.getSelection();
				adjustments[1] = rightInput.getSelection();
				adjustments[2] = topInput.getSelection();
				adjustments[3] = bottomInput.getSelection();
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
		
		return adjustments;
	}
	
	private Spinner getSpinner(Composite parent, String text) {
		Composite spinnerBox = new Composite(parent, SWT.NONE);
		spinnerBox.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false));
		spinnerBox.setLayout(new GridLayout(2, false));
		Label label = new Label(spinnerBox, SWT.CENTER);
		label.setText(text + ":");			
		Spinner spinner = new Spinner(spinnerBox, SWT.NONE);
		spinner.setMaximum(32);
		spinner.setMinimum(-16);
		spinner.setSelection(ZERO);
		return spinner;
	}
}

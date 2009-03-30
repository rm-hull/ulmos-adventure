# compile everything to java classes

SWT_JAR="$HOME/.m2/repository/org/eclipse/swt/carbon/gtk/3.4.0/gtk-3.4.0.jar"
EDITOR_JAR="$HOME/workspaces/dev/editor/target/editor-1.0.jar"

groovyc -classpath $SWT_JAR:$EDITOR_JAR:./bin-groovy src/*.groovy -d bin-groovy

# run as java

GROOVY_JAR="$HOME/Java/groovy-1.5.6/embeddable/groovy-all-1.5.6.jar"
RESOURCES="$HOME/workspaces/dev/editor/src/test/resources/"

java -cp $GROOVY_JAR:$SWT_JAR:$EDITOR_JAR:$RESOURCES:./bin-groovy GRpgEditor
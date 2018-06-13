import org.pmw.tinylog.Configurator
import org.pmw.tinylog.Level
import org.pmw.tinylog.writers.FileWriter
import org.pmw.tinylog.writers.ConsoleWriter
import java.io.File

class Settings(val interval: Int,
               val threadPoolSize: Int,
               val logFile:String,
               val isDebug: Boolean,
               val areaIDs: List<String>,
               val specializationsIDs: List<String>,
               val appName: String,
               val appEmail: String,
               val version: String) {
    private val loggerFormat = "{date:yyyy-MM-dd HH:mm:ss} {message}"
    val defaultHeaders = HashMap<String, String>()

    init {
        defaultHeaders["user-agent"] = "$appName/$version ($appEmail)"
        if (isDebug) {
            Configurator.defaultConfig()
                    .formatPattern(loggerFormat)
                    .writer(FileWriter(logFile, true, true))
                    .addWriter(ConsoleWriter())
                    .level(Level.DEBUG).activate()
        } else {
            Configurator.defaultConfig()
                    .formatPattern(loggerFormat)
                    .writer(FileWriter(logFile, true, true))
                    .addWriter(ConsoleWriter())
                    .level(Level.INFO).activate()
        }
    }

    override fun toString(): String {
        return "Settings(interval=$interval, threadPoolSize=$threadPoolSize, logFile='$logFile', isDebug=$isDebug, areaIDs=$areaIDs, specializationsIDs=$specializationsIDs, appName='$appName', appEmail='$appEmail', version='$version', loggerFormat='$loggerFormat', defaultHeaders=$defaultHeaders)"
    }

}
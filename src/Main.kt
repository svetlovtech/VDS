import org.pmw.tinylog.Logger
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.Executors

fun main(args: Array<String>) {
    val settingsStream = Settings::class.java.getResourceAsStream("settings.prop")
    val properties = Properties()
    properties.load(settingsStream)
    val settings = Settings(
            interval = properties.getProperty("interval").toInt(),
            threadPoolSize = properties.getProperty("threadPoolSize").toInt(),
            logFile = properties.getProperty("logFile"),
            isDebug = properties.getProperty("isDebug").toBoolean(),
            areaIDs = properties.getProperty("areaIDs").split(","),
            specializationsIDs = properties.getProperty("specializationsIDs").split(","),
            appName = properties.getProperty("appName"),
            appEmail = properties.getProperty("appEmail"),
            version = properties.getProperty("version"))
    Logger.info("Starting VDS...")
    Logger.info("settings = $settings")
    val dataFileName = File(properties.getProperty("dataFileName"))
    Logger.info("Creating data file (${dataFileName.name})...")
    dataFileName.createNewFile()
    while (true){
        Logger.info("Parsing data ...")
        val currentDateTime = Date()
        val api = HHApiUtils(settings)
        api.getAreas(currentDateTime)
        api.getSpecializations(currentDateTime)
        val vacanciesUrls = api.getVacanciesList(currentDateTime)
        val vacanciesList = ArrayList<Vacancy>()
        for (url in vacanciesUrls) {
            vacanciesList.add(Vacancy(url, settings, currentDateTime, dataFileName))
        }
        val threadPool = Executors.newFixedThreadPool(settings.threadPoolSize)
        for (vacancy in vacanciesList) {
            threadPool.submit(vacancy)
        }
        threadPool.shutdown()
        while (!threadPool.isTerminated) {
            Thread.sleep(1000)
            Logger.info("$StatCounter from ${vacanciesList.size}")
        }
        StatCounter.clearAll()
        Logger.info("Parsing data complete")
        Thread.sleep((1000 * settings.interval).toLong())
    }

}
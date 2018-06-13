import com.mashape.unirest.http.Unirest
import org.json.JSONException
import org.json.JSONObject
import org.pmw.tinylog.Logger
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

class HHApiUtils(private val settings: Settings) {
    private val defaultDateTimeFormat = SimpleDateFormat("yyyyMMdd_HHmmss")
    private val defaultHeaders = HashMap<String, String>()
    private val maxDataUnitsPerPage = 100

    fun getAreas(currentDateTime: Date) {
        val response = Unirest
                .get("https://api.hh.ru/areas")
                .headers(defaultHeaders).asJson()
        val areasFile = File("${defaultDateTimeFormat.format(currentDateTime)}_Areas.txt")
        areasFile.createNewFile()
        areasFile.appendText(response.body.toString())

    }

    fun getSpecializations(currentDateTime: Date) {
        val response = Unirest
                .get("https://api.hh.ru/specializations")
                .headers(defaultHeaders).asJson()
        val specFile = File("${defaultDateTimeFormat.format(currentDateTime)}_Specializations.txt")
        specFile.createNewFile()
        specFile.appendText(response.body.toString())
    }

    fun getVacanciesList(currentDateTime: Date): Set<String> {
        val vacanciesUrlArray = ArrayList<String>()
        for (area in settings.areaIDs) {
            Logger.info("Getting URL from area $area")
            for (specialization in settings.specializationsIDs) {
                Logger.info("\tGetting URL from specialization $specialization")
                var pageNumber = 0
                while (true) {
                    Logger.info("\t\tGetting page№$pageNumber")
                    val response = Unirest.get("https://api.hh.ru/vacancies")
                            .headers(defaultHeaders)
                            .queryString("area", area)
                            .queryString("specialization", specialization)
                            .queryString("page", pageNumber.toString())
                            .queryString("per_page", maxDataUnitsPerPage)
                            .queryString("no_magic", "true")
                            .queryString("period", "1")
                            .asJson()
                    val items = response.body.`object`.getJSONArray("items")
                    try {
                        for (x in 0 until maxDataUnitsPerPage) {
                            val obj: JSONObject = items[x] as JSONObject
                            vacanciesUrlArray.add(obj.get("url").toString())
                        }
                        pageNumber++
                    } catch (e: JSONException) {
                        pageNumber++
                    }
                    if (pageNumber == response.body.`object`["pages"]) {
                        break
                    }
                }
            }
        }
        val sortedUrlArray = vacanciesUrlArray.toSet()
        Logger.info("all_vacancies ${vacanciesUrlArray.size}")
        Logger.info("unique_vacancies ${sortedUrlArray.size}")
        return sortedUrlArray
    }
}
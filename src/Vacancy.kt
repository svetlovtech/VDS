import com.mashape.unirest.http.Unirest
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

class Vacancy(private val url: String,
              private val settings: Settings,
              private val currentDateTime: Date,
              private val dataFile: File) : Runnable {
    private val timeFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
    override fun run() {
        val response = Unirest
                .get(url)
                .headers(settings.defaultHeaders).asJson()
        dataFile.appendText("${timeFormat.format(currentDateTime)} Vacancy: ${response.body.toString().toLowerCase()}\n")
        StatCounter.incrementVacancyPoint()
    }
}
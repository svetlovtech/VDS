import java.util.concurrent.atomic.AtomicInteger

class StatCounter {
    companion object {
        private var vacancy = AtomicInteger()

        fun incrementVacancyPoint() {
            vacancy.incrementAndGet()
        }

        fun clearAll() {
            vacancy.set(0)
        }

        override fun toString(): String {
            return "StatCounter(vacancy=$vacancy)"
        }
    }
}
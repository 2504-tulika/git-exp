import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import com.tulika.todoapp.entity.Status;

public class TodoDTO {

    @NotNull
    @Size(min = 3, message = "Title must be at least 3 characters")
    private String title;

    private String description;

    private Status status;

    // Getters & Setters
    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Status getStatus() {
        return status;
    }

    public void setStatus(Status status) {
        this.status = status;
    }
}
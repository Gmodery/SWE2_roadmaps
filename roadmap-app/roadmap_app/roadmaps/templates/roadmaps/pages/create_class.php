<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Save Class</button>
</form>
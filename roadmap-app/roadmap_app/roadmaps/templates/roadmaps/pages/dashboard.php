<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>

<body>
    <div class="dashboard-container">
        <h2>Welcome, {{ username }}!</h2>
        <a href="{% url 'logout' %}">Logout</a>
    </div>
</body>

</html>
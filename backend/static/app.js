async function loadUsers() {
  const res = await fetch("/users");
  const users = await res.json();

  const list = document.getElementById("users");
  list.innerHTML = "";

  users.forEach(u => {
    const li = document.createElement("li");
    li.textContent = u.name;
    list.appendChild(li);
  });
}

async function addUser() {
  const nameInput = document.getElementById("name");
  const name = nameInput.value;

  if (!name) return;

  await fetch("/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  });

  nameInput.value = "";
  loadUsers();
}

loadUsers();

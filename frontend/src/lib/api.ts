const API_URL = "http://localhost:8000/api";

export async function uploadFile(file: File, password?: string) {
    const formData = new FormData();
    formData.append("file", file);
    if (password) {
        formData.append("password", password);
    }

    const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error("Upload failed");
    }

    return response.json();
}

export async function getTransactions() {
    const response = await fetch(`${API_URL}/transactions`);
    if (!response.ok) {
        throw new Error("Failed to fetch transactions");
    }
    return response.json();
}

export async function getFiles() {
    const response = await fetch(`${API_URL}/files`);
    if (!response.ok) {
        throw new Error("Failed to fetch files");
    }
    return response.json();
}

export async function deleteFile(filename: string) {
    const response = await fetch(`${API_URL}/files/${filename}`, {
        method: "DELETE",
    });
    if (!response.ok) {
        throw new Error("Failed to delete file");
    }
    return response.json();
}

const pid = "01a19272-ddb2-719e-82ba-e292968d0e25";

const deleteProduct = async () => {
  try {
    const response = await fetch(
      `http://127.0.0.1:8000/delete-product/${pid}`,
      {
        method: "DELETE",
      },
    );
    return await response.json();
  } catch (error) {
    return { success: false, message: "Network Error", error };
  }
};

const testDeleteRaceCondition = async () => {
  console.log("🚀 Firing 5 simultaneous DELETE requests...");

  const results = await Promise.all([
    deleteProduct(),
    deleteProduct(),
    deleteProduct(),
    deleteProduct(),
    deleteProduct(),
  ]);

  results.forEach((data, index) => {
    console.log(`\n--- Request ${index + 1} Result ---`);
    console.log(data);
  });
};

testDeleteRaceCondition();

const mysql = require('mysql');

const connection = mysql.createConnection({
  host: '192.168.1.3', // Replace with your actual host
  user: 'admin', // Replace with your actual username
  password: '123456', // Replace with your actual password
  database: 'document_management' // Replace with your actual database name
});

// // Define the table name and column definitions
// const tableName = 'my_table';
// const columns = {
//   id: {
//     type: 'int',
//     primary_key: true,
//     auto_increment: true
//   },
//   name: {
//     type: 'varchar(50)',
//     not_null: true
//   },
//   age: {
//     type: 'int'
//   }
// };

// // Generate the CREATE TABLE statement
// const createTableSql = `CREATE TABLE ${tableName} (`;
// for (const column in columns) {
//   createTableSql += `\n  ${column} ${columns[column].type}`;
//   if (columns[column].primary_key) {
//     createTableSql += ' PRIMARY KEY';
//   }
//   if (columns[column].auto_increment) {
//     createTableSql += ' AUTO_INCREMENT';
//   }
//   if (columns[column].not_null) {
//     createTableSql += ' NOT NULL';
//   }
//   createTableSql += ',';
// }
// // Remove the trailing comma and add the closing parenthesis
// createTableSql = createTableSql.slice(0, -1) + ')';

// // Connect to the database
// connection.connect(err => {
//   if (err) {
//     console.error(err);
//     return;
//   }
//   console.log('Connected to MySQL database');

//   // Create the table
//   connection.query(createTableSql, err => {
//     if (err) {
//       console.error(err);
//       return;
//     }
//     console.log(`Table ${tableName} created successfully`);
//   });

//   // Close the connection
//   connection.end();
// });

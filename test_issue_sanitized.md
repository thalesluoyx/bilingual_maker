
As Example 5.6 shows, we apply the View Helper pattern, changing the design and extracting scriptlet code from the JSP view.  

如示例5.6所示，我们应用了视图助手模式，通过改变设计将脚本代码从JSP视图中抽离出来。

# Example 5.6 JSP with Scriptlet Code Extracted  

&lt;%@ taglib uri =$ "/WEB-INF/corepatternstaglibrary.tld" prefix = "corepatterns" %&gt;   
<html>   
<head><title>Employee List</title></head>   
<body>   
&lt;corepatterns:employeeAdapter /&gt;   
<h3><center>List of employees in &lt;corepatterns:department attribute =$ "id"/&gt; department - Using Custom Tag Helper Strategy </h3>   
&lt;table border =$ "1" &gt; <tr> <th> First Name </th> <th> Last Name </th> <th> Designation </th> <th> Employee Id </th> <th> Tax Deductibles </th> <th> Performance Remarks </th> <th> Yearly Salary</th> </tr> &lt;corepatterns:employeelist id = "employeelist_key"&gt; <tr> <td>&lt;corepatterns:employee attribute =$ "FirstName"/&gt;</td> <td>&lt;corepatterns:employee attribute =$ "LastName"/&gt;</td> <td>&lt;corepatterns:employee attribute =$ "Designation"/&gt; </td> <td>&lt;corepatterns:employee attribute =$ "Id"/&gt;</td> <td>&lt;corepatterns:employee attribute =$ "NoOfDeductibles"/&gt;</td> <td>&lt;corepatterns:employee attribute =$ "PerformanceRemarks"/&gt;</td> <td>&lt;corepatterns:employee attribute =$ "YearlySalary"/&gt;</td> <td> </tr> &lt;/corepatterns:employeelist&gt;   
</table>   
</body>   
</html>  

&lt;%@ taglib uri="/WEB-INF/corepatternstaglibrary.tld" prefix="corepatterns" %&gt;  
<html>  
<head><title>员工列表</title></head>  
<body>  
&lt;corepatterns:employeeAdapter /&gt;  
<h3><center>&lt;corepatterns:department attribute="id"/&gt; 部门员工列表 - 采用自定义标签辅助策略</h3>  
<table border="1">  
<tr>  
<th>名</th>  
<th>姓</th>  
<th>职位</th>  
<th>员工编号</th>  
<th>税务抵扣项</th>  
<th>绩效评语</th>  
<th>年薪</th>  
</tr>  
&lt;corepatterns:employeelist id="employeelist_key"&gt;  
<tr>  
<td>&lt;corepatterns:employee attribute="FirstName"/&gt;</td>  
<td>&lt;corepatterns:employee attribute="LastName"/&gt;</td>  
<td>&lt;corepatterns:employee attribute="Designation"/&gt;</td>  
<td>&lt;corepatterns:employee attribute="Id"/&gt;</td>  
<td>&lt;corepatterns:employee attribute="NoOfDeductibles"/&gt;</td>  
<td>&lt;corepatterns:employee attribute="PerformanceRemarks"/&gt;</td>  
<td>&lt;corepatterns:employee attribute="YearlySalary"/&gt;</td>  
</tr>  
&lt;/corepatterns:employeelist&gt;  
</table>  
</body>  
</html>

Additionally, we have written two custom tag helpers to encapsulate our business and presentation formatting processing logic by adapting the data model into the rows and columns of our HTML table.  

此外，我们还编写了两个自定义标签助手，通过将数据模型适配到HTML表格的行列结构中，封装了业务与展示层的格式化处理逻辑。

<?xml version="1.0"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns="http://www.w3.org/1999/xhtml">

<xsl:import href="resource:templates/reST.xsl" />

<xsl:template match="step" name="step">
  <div class="step">
    <xsl:copy-of select="@*"/>
    <xsl:apply-templates />
  </div>
</xsl:template>

<xsl:template match="note" name="note">
  <div class="notes"><xsl:apply-templates /></div>
</xsl:template>

<xsl:template match="/" name="main">
<html>
  <head>
    <title><xsl:value-of select="/document/@title"/></title>

    <meta charset="UTF-8"/>
    <meta name="generator" content="prezentprogramo 1.0 https://github.com/yoosofan/prezentprogramo"/>
    <xsl:if test="/document/author"> <!-- Author is a child to the document, everything else become attributes -->
      <meta name="author">
        <xsl:attribute name="content">
          <xsl:value-of select="/document/author" />
        </xsl:attribute>
      </meta>
    </xsl:if>
    <xsl:if test="/document/@description">
      <meta name="description">
        <xsl:attribute name="content">
          <xsl:value-of select="/document/@description" />
        </xsl:attribute>
      </meta>
    </xsl:if>
    <xsl:if test="/document/@keywords">
      <meta name="keywords">
        <xsl:attribute name="content">
          <xsl:value-of select="/document/@keywords" />
        </xsl:attribute>
      </meta>
    </xsl:if>

    <xsl:for-each select="/document/templateinfo/header/css">
      <link rel="stylesheet">
        <xsl:copy-of select="@*"/>
      </link>
    </xsl:for-each>

    <script type="text/x-mathjax-config">
      MathJax.Hub.Config({
        showProcessingMessages: false,
        messageStyle: "none",
        TeX : { extensions : ['color.js'] }
      });
    </script>

    <xsl:for-each select="/document/templateinfo/header/js">
      <script type="text/javascript">
        <xsl:copy-of select="@*"/>
      </script>
    </xsl:for-each>


  </head>
  <body class="impress-not-supported">
    <xsl:if test="not(/document/@skip-help)">
      <div id="impress-help"/>
    </xsl:if>
    <xsl:for-each select="/document">
      <xsl:for-each select="decoration/header">
        <div class="header">
          <xsl:apply-templates />
        </div>
      </xsl:for-each>

      <div id="impress">
        <xsl:if test="@data-width">
          <xsl:attribute name="data-width">
            <xsl:value-of select="@data-width" />
          </xsl:attribute>
        </xsl:if>
        <xsl:if test="@data-height">
          <xsl:attribute name="data-height">
            <xsl:value-of select="@data-height" />
          </xsl:attribute>
        </xsl:if>
        <xsl:if test="@data-max-scale">
          <xsl:attribute name="data-max-scale">
            <xsl:value-of select="@data-max-scale" />
          </xsl:attribute>
        </xsl:if>
        <xsl:if test="@data-min-scale">
          <xsl:attribute name="data-min-scale">
            <xsl:value-of select="@data-min-scale" />
          </xsl:attribute>
        </xsl:if>
        <xsl:if test="@data-perspective">
          <xsl:attribute name="data-perspective">
            <xsl:value-of select="@data-perspective" />
          </xsl:attribute>
        </xsl:if>
        <xsl:if test="@data-transition-duration">
          <xsl:attribute name="data-transition-duration">
            <xsl:value-of select="@data-transition-duration" />
          </xsl:attribute>
        </xsl:if>
        <xsl:if test="@auto-console">
          <xsl:attribute name="auto-console">
            <xsl:value-of select="@auto-console" />
          </xsl:attribute>
        </xsl:if>
        <xsl:if test="/document/@css-console">
          <xsl:attribute name="data-console-css">
            <xsl:value-of select="/document/@css-console" />
          </xsl:attribute>
        </xsl:if>
        <xsl:if test="/document/@css-preview">
          <xsl:attribute name="data-console-css-iframe">
            <xsl:value-of select="/document/@css-preview" />
          </xsl:attribute>
        </xsl:if>
        <xsl:for-each select="step">
          <div class="step">
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates />
          </div>
        </xsl:for-each>
      </div>
      <xsl:for-each select="decoration/footer">
        <div class="footer">
          <xsl:apply-templates />
        </div>
      </xsl:for-each>
    </xsl:for-each>
    <xsl:if test="/document/@slide-numbers">
      <div id="slide-number" class="slide-number">
         1
      </div>
    </xsl:if>

    <xsl:for-each select="/document/templateinfo/body/js">
      <script type="text/javascript">
        <xsl:copy-of select="@*"/>
      </script>
    </xsl:for-each>
    <xsl:if test="/document/@slide-numbers">
    <script type="text/javascript">
      document.getElementById("impress").addEventListener("impress:stepenter", update_slide_number, false);
    </script>
  </xsl:if>

</body>
</html>
</xsl:template>

</xsl:stylesheet>
